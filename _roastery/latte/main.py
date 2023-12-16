import re
import os
from agents.baseline import BaselineAgent
from agents.latte_art import LatteAgent
from agents.component_path import ComponentPathAgent
from file_watcher import FileWatcher
import shutil
import json
from pydantic import BaseModel
from typing import Optional
import asyncio

CodeAgent = BaselineAgent()
PathAgent = ComponentPathAgent()
LatteAgent = LatteAgent()

class FileContext(BaseModel):
    file_path: str
    file_content: str
    root_directory: str
    mount_dir: str
    working_dir: str
    example_content: Optional[str] = None

class BrewContext(FileContext):
    brew_path: str
    brew_content: str
    coffee_import_statement: str
    coffee_tag: dict

class SteamContext(FileContext):
    latte_import_statement: str
    latte_tag: dict
    steam_path: str
    steam_content: str

async def process_file(file_path, mount_dir=None, root_directory=None, example=None):
    """
    Detects and processes <Coffee> and <Component coffee="..."> tags.
    """
    with open(file_path, "r") as file:
        file_content = file.read()

    example_content = None
    if example:
        example_path = os.path.join(root_directory, "./"+example)
        try:
            with open(example_path, "r") as example_file:
                example_content = example_file.read()
        except FileNotFoundError:
            print(f"Could not find example file at {example_path}")
            return

    ctx = FileContext(
        file_path=file_path,
        file_content=file_content,
        root_directory=root_directory,
        mount_dir=mount_dir,
        working_dir=os.path.join(os.path.dirname(file_path), mount_dir),
        example_content=example_content,
    )

    # Extract and process <Coffee> tag
    coffee_tag = extract_tag(file_content, tag="Coffee")
    if coffee_tag:
        print(f"<Coffee> tag found in {file_path}")
        process_coffee_tag(coffee_tag=coffee_tag, ctx=ctx)

    # Extract and process <Latte> tag
    latte_tag = extract_tag(file_content, tag="Latte")
    if latte_tag:
        print(f"<Latte> tag found in {file_path}")
        await process_latte_tag(latte_tag=latte_tag, ctx=ctx)

    # Extract and process <Component coffee="..."> caffeniated components
    caffeinated_component = extract_tag(
        file_content, attribute="coffee=[\"'][^\"']+[\"']"
    )
    if caffeinated_component:
        print(f"Caffeinated component found in {file_path}")
        proccess_caffeinated_component(
            caffeinated_component=caffeinated_component, ctx=ctx
        )
        return


def process_coffee_tag(coffee_tag=None, ctx: FileContext = None):
    """
    Brews or Pours <Coffee> components.
    """
    working_dir = os.path.join(os.path.dirname(ctx.file_path), ctx.mount_dir)
    coffee_import_statement = f"import Coffee from '{ctx.mount_dir}/Coffee'\n"
    extension = ctx.file_path.split(".")[-1]
    brew_path = os.path.join(working_dir, "Brew."+extension)
    brew_content = ""

    if os.path.exists(brew_path):
        with open(brew_path, "r") as brew_file:
            brew_content = brew_file.read()
    brew_ctx = BrewContext(
        **ctx.dict(),
        brew_path=brew_path,
        brew_content=brew_content,
        coffee_import_statement=coffee_import_statement,
        coffee_tag=coffee_tag,
    )
    pour = coffee_tag["props"].get("pour", None)

    if pour:
        print(f"Pouring component to {pour}...")
        mount_files("./mount", working_dir, False, cleanup=[brew_path])
        pour_component(pour_path=pour, ctx=brew_ctx)
    else:
        print("Brewing new component...")
        mount_files("./mount", working_dir, True, without=[".d.ts"] if extension not in ["ts", "tsx"] else [])
        brew_component(ctx=brew_ctx)

    return

async def process_latte_tag(latte_tag=None, ctx: FileContext = None):
    """
    Steams or pours <Latte> components.
    """
    working_dir = os.path.join(os.path.dirname(ctx.file_path), ctx.mount_dir)
    latte_import_statement = f"import Latte from '{ctx.mount_dir}/Latte'\n"
    extension = ctx.file_path.split(".")[-1]
    steam_path = os.path.join(working_dir, "Steam."+extension)
    steam_content = ""

    if os.path.exists(steam_path):
        with open(steam_path, "r") as brew_file:
            steam_content = brew_file.read()

    steam_path = os.path.join(working_dir, "Steam.tsx")
    steam_ctx = SteamContext(
        **ctx.dict(),
        steam_path=steam_path,
        steam_content=steam_content,
        latte_import_statement=latte_import_statement,
        latte_tag=latte_tag,
    )
    pour = latte_tag["props"].get("pour", None)

    if pour:
        print(f"pouring image...")
        mount_files("./mount", working_dir, False, cleanup=[steam_path])
        await pour_latte_art(pour_path=pour, ctx=steam_ctx)
    else:
        print("Steaming new image...")
        mount_files("./mount", working_dir, True, without=[".d.ts"] if extension not in ["ts", "tsx"] else [])
        await steam_component(ctx=steam_ctx)

    return

def brew_component(ctx: BrewContext = None):
    file_content, modified = set_import(
        ctx.file_content, ctx.coffee_import_statement, True
    )
    if modified:
        with open(ctx.file_path, "w") as file:
            file.write(file_content)

    prompt = ctx.coffee_tag["children"]

    for update in CodeAgent.modify_file(
        source_file=ctx.brew_path,
        user_query=prompt,
        file_content=ctx.brew_content,
        parent_file_content=file_content,
        example_content=ctx.example_content,
    ):
        print(update)


async def steam_component(ctx: SteamContext = None):
    file_content, modified = set_import(
        ctx.file_content, ctx.latte_import_statement, True
    )
    if modified:
        with open(ctx.file_path, "w") as file:
            file.write(file_content)

    prompt = ctx.latte_tag["children"]
    await LatteAgent.generate_latte_art(prompt=prompt, steam_path=ctx.steam_path)

def pour_component(
    pour_path=None, attributes_to_remove=["brew", "pour"], ctx: BrewContext = None
):
    """
    Replaces the <Coffee> tag with <BrewedComponent>.
    1. Replace <Coffee ...> </Coffee> tag with <ComponentName ...props />
    2. Append import ComponentName from './coffee/brew/ComponentName' after the last import statement.
    """

    # Replace tag
    component_name = pour_path.split(".")[0]
    coffee_start, coffee_end = ctx.coffee_tag["match"].span()
    attributes = ctx.coffee_tag["attributes"]
    for attr in attributes_to_remove:
        attributes = re.sub(rf'\b{attr}="[^"]+"\s*|\b{attr}\b\s*', "", attributes)
    file_content = ctx.file_content
    file_content = (
        file_content[:coffee_start]
        + f"<{component_name} {attributes.strip()} />"
        + file_content[coffee_end:]
    )

    # Update import statements
    import_statement = (
        f"import {component_name} from '{ctx.mount_dir}/{component_name}'\n"
    )
    file_content, _ = set_import(file_content, import_statement, True)
    file_content, _ = set_import(file_content, ctx.coffee_import_statement, False)

    # Create component file
    component_file_path = os.path.join(
        os.path.dirname(ctx.file_path), ctx.mount_dir, pour_path
    )
    with open(component_file_path, "w") as component_file:
        component_file.write(ctx.brew_content)

    # Update parent file
    with open(ctx.file_path, "w") as file:
        file.write(file_content)

    # Update component file to reflect the new name
    for update in CodeAgent.modify_file(
        source_file=component_file_path,
        user_query=f'Update component file to reflect the new component name: {component_name}',
        file_content=ctx.brew_content,
        parent_file_content=file_content,
        example_content=ctx.example_content,
    ):
        print(update)

    print("Replacement complete.")


async def pour_latte_art(
  pour_path=None, attributes_to_remove=["brew", "pour"], ctx: SteamContext = None
):
  """
  Replaces the <Latte> tag with <SteamedComponent>.
  1. Replace <Coffee ...> </Coffee> tag with <ComponentName ...props />
  2. Append import ComponentName from './coffee/brew/ComponentName' after the last import statement.
  """

  # Replace tag
  component_name = pour_path.split(".")[0]
  latte_start, latte_end = ctx.latte_tag["match"].span()
  attributes = ctx.latte_tag["attributes"]
  for attr in attributes_to_remove:
      attributes = re.sub(rf'\b{attr}="[^"]+"\s*|\b{attr}\b\s*', "", attributes)
  file_content = ctx.file_content
  file_content = (
      file_content[:latte_start]
      + f"<{component_name} {attributes.strip()} />"
      + file_content[latte_end:]
  )

  # Update import statements
  import_statement = (
      f"import {component_name} from '{ctx.mount_dir}/{component_name}'\n"
  )
  file_content, _ = set_import(file_content, import_statement, True)
  file_content, _ = set_import(file_content, ctx.latte_import_statement, False)

  # Create component file
  component_file_path = os.path.join(
      os.path.dirname(ctx.file_path), ctx.mount_dir, pour_path
  )
  with open(component_file_path, "w") as component_file:
      component_file.write(ctx.steam_content)

  src_pattern = r'src="([^"]+)"'
  src_match = re.search(src_pattern, ctx.steam_content)

  # Update parent file
  with open(ctx.file_path, "w") as file:
      file.write(file_content)

  if src_match:
      src_value = src_match.group(1)
      print(f'src attribute value: {src_value}')
      await LatteAgent.save_img(src_value, component_name, ctx.file_path, ctx.mount_dir)

  print("Replacement complete.")


def proccess_caffeinated_component(caffeinated_component=None, ctx: FileContext = None):
    component_name = caffeinated_component["tag"]
    import_pattern = rf"({component_name})(.*?)from\s[\'\"](.*?)[\'\"]"
    match = re.search(import_pattern, ctx.file_content, re.DOTALL)

    if not match:
        print(f"Could not find import statement for {component_name}")
        return

    component_file_path = None
    for update in PathAgent.run(
        component=component_name,
        parent_file_path=ctx.file_path,
        import_statement=match.group(0),
        directory=root_directory,
    ):
        print(update)
        if isinstance(update, dict) and update.get("file_path"):
            component_file_path = update["file_path"]

    if not component_file_path:
        print(f"Could not find component file for {component_name}")
        return

    with open(component_file_path, "r") as component_file:
        component_file_content = component_file.read()
        if not component_file_content:
            # TODO: handle back-and-forth with agent if file content is not found
            print(
                f"Could not read component file for {component_name} at {component_file_path}"
            )
            return

    for update in CodeAgent.modify_file(
        user_query=caffeinated_component["props"]["coffee"],
        source_file=component_file_path,
        file_content=component_file_content,
        parent_file_content=ctx.file_content,
        example_content=ctx.example_content,
    ):
        print(update)


def extract_tag(file_content, tag="\w+", attribute=""):
    """
    Extracts a tag from the file content based on the tag name and additional attributes.
    """
    pattern = rf"<({tag})\s?([^>/]*?{attribute}[^>/]*)(?:>(.*?)</{tag}>|/>)"
    match = re.search(pattern, file_content, re.DOTALL)

    if match:
        tag_name, attributes, content = match.groups()
        props = {
            m[0]: m[1] or True
            for m in re.findall(r'(\w+)(?:=["\']([^"\']+)["\']|\b)', attributes)
        }
        return {
            "match": match,
            "tag": tag_name,
            "props": props,
            "children": content.strip() if content else "",
            "attributes": attributes,
        }

    return None


def set_import(file_content, import_statement, upsert=True):
    """
    Adds or removes the import statements from file_content.
    """
    remove = not upsert
    import_index = file_content.find(import_statement)
    modified = False

    if remove and import_index != -1:
        file_content = (
            file_content[:import_index]
            + file_content[import_index + len(import_statement) :]
        )
        modified = True
    if upsert and import_index == -1:
        insert_index = file_content.find("\n", file_content.find("from", file_content.rfind("import ")))
        file_content = (
            file_content[: insert_index + 1]
            + import_statement
            + file_content[insert_index + 1 :]
        )
        modified = True

    return file_content, modified


def mount_files(source, target, mount=True, cleanup=[], without=[]):
    """
    Mount or unmount the source directory to the target directory.
    """
    if mount and not os.path.exists(target):
        os.makedirs(target)
    for item in os.listdir(source):
        s = os.path.join(source, item)
        d = os.path.join(target, item)

        if any(s.endswith(ext) for ext in without):
            continue

        if os.path.isdir(s):
            os.symlink(s, d) if mount else os.remove(d)
        else:
            shutil.copy2(s, d) if mount else os.remove(d)

    if not mount and len(cleanup):
        for path in cleanup:
          if os.path.exists(path):
            os.remove(path)

def parse_config(path):
    """
    Reads and parses config file
    """

    default_config = {"mount": "./components", "patterns": ["**/*.js","**/*.jsx", "**/*.ts", "**/*.tsx"], "example": None}
    try:
        with open(path, "r") as file:
            return dict(default_config, **json.load(file))
    except FileNotFoundError:
        return default_config


async def main():
    watcher = None

    if watcher:
        print("Hot reloading...")
        watcher.stop()

    print("Starting...")
    root_directory = os.environ.get("ROOT_DIR", "/mount")
    config = parse_config(root_directory + "/coffee.config.json")

    watcher = FileWatcher(
        root_directory,
        watch_patterns=config["patterns"],
        ignore_patterns=["Coffee.jsx", "Coffee.d.ts", "Brew.*"],
    )
    watcher.start()
    prev_inc = 0

    try:
        while True:
            await asyncio.sleep(1)
            if prev_inc != watcher.last_modified_file_inc:
                print(f"File changed: {watcher.last_modified_file}")
                await process_file(
                    watcher.last_modified_file,
                    mount_dir=config["mount"],
                    root_directory=root_directory,
                    example=config["example"],
                )
                prev_inc = watcher.last_modified_file_inc
    finally:
        watcher.stop()

if __name__ == "__main__":
    try:
      asyncio.run(main())
    except KeyboardInterrupt:
      print("Stopping due to KeyboardInterrupt...")

