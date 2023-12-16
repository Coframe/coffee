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

class CaffeineContext(FileContext):
    path: str
    content: str
    tag_import_statement: str
    tag: dict

caffeine_component = {
    "Latte": "Steam",
    "Coffee": "Brew",
}

async def process_file(file_path, mount_dir=None, root_directory=None, example=None):
    """
    Detects and processes <Coffee>, <Component coffee="...">, and <Latte> tags.
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

    # Extract and process <Coffee> or <Latte> tag
    coffee_tag = extract_tag(file_content, tag="Coffee")
    latte_tag = extract_tag(file_content, tag="Latte")

    if coffee_tag:
        print(f"<Coffee> tag found in {file_path}")
        await process_tag(tag=coffee_tag, ctx=ctx)
    if latte_tag:
        print(f"<Latte> tag found in {file_path}")
        await process_tag(tag=latte_tag, ctx=ctx)

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


async def process_tag(tag=None, ctx: FileContext = None):
    """
    Processes <Coffee> or <Latte> components.
    """
    working_dir = os.path.join(os.path.dirname(ctx.file_path), ctx.mount_dir)
    tag_name, caffeine_tag_name = tag["tag"], caffeine_component[tag["tag"]]
    tag_import_statement = f"import {tag_name} from '{ctx.mount_dir}/{tag_name}'\n"
    extension = ctx.file_path.split(".")[-1]
    caffeine_path = os.path.join(working_dir, f"{caffeine_tag_name}.{extension}")
    caffeine_content = ""

    if os.path.exists(caffeine_path):
        with open(caffeine_path, "r") as caffeine_file:
            caffeine_content = caffeine_file.read()

    caffeine_ctx = CaffeineContext(
        **ctx.dict(),
        path=caffeine_path,
        content=caffeine_content,
        tag_import_statement=tag_import_statement,
        tag=tag,
    )
    pour = tag["props"].get("pour", None)
    print('pour', pour)

    if pour:
        print(f"Pouring component to {pour}...")
        mount_files("./mount", working_dir, False, cleanup=[caffeine_path])
        await pour_component(pour_path=pour, ctx=caffeine_ctx)
    else:
        print(f"Processing new {tag_name} component...")
        mount_files("./mount", working_dir, True, without=[".d.ts"] if extension not in ["ts", "tsx"] else [])
        await brew_component(ctx=caffeine_ctx)

    return

async def brew_component(ctx: CaffeineContext = None):
    file_content, modified = set_import(
        ctx.file_content, ctx.tag_import_statement, True
    )
    if modified:
        with open(ctx.file_path, "w") as file:
            file.write(file_content)

    prompt = ctx.tag["children"]

    if ctx.tag["tag"] == "Latte":
      await LatteAgent.generate_latte_art(prompt=prompt, steam_path=ctx.path)
    else:
      for update in CodeAgent.modify_file(
          source_file=ctx.path,
          user_query=prompt,
          file_content=ctx.content,
          parent_file_content=file_content,
          example_content=ctx.example_content,
      ):
          print(update)


async def pour_component(
    pour_path=None,
    attributes_to_remove=["brew", "pour"],
    ctx=None,
):
    """
    Replaces the <Coffee> or <Latte> tag with <Component>.
    1. Replace <Coffee ...> </Coffee> tag with <ComponentName ...props />
    2. Append import ComponentName from './mount_dir/ComponentName' after the last import statement.
    """

    # Replace tag
    component_name = pour_path.split(".")[0]
    tag_start, tag_end = ctx.tag["match"].span()
    attributes = ctx.tag["attributes"]
    for attr in attributes_to_remove:
        attributes = re.sub(rf'\b{attr}="[^"]+"\s*|\b{attr}\b\s*', "", attributes)
    file_content = ctx.file_content
    file_content = (
        file_content[:tag_start]
        + f"<{component_name} {attributes.strip()}/>"
        + file_content[tag_end:]
    )

    # Update import statements
    import_statement = (
        f"import {component_name} from '{ctx.mount_dir}/{component_name}'\n"
    )
    file_content, _ = set_import(file_content, import_statement, True)
    file_content, _ = set_import(file_content, ctx.tag_import_statement, False)

    # Create component file
    component_file_path = os.path.join(
        os.path.dirname(ctx.file_path), ctx.mount_dir, pour_path
    )
    with open(component_file_path, "w") as component_file:
        component_file.write(ctx.content)

    # Update parent file
    with open(ctx.file_path, "w") as file:
        file.write(file_content)

    # Update component file to reflect the new name
    for update in CodeAgent.modify_file(
        source_file=component_file_path,
        user_query=f'Update component file to reflect the new component name: {component_name}',
        file_content=ctx.content,
        parent_file_content=file_content,
        example_content=ctx.example_content,
    ):
        print(update)

    if ctx.tag["tag"] == "Latte":
        src_pattern = r'src="([^"]+)"'
        src_match = re.search(src_pattern, ctx.content)
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
        directory=os.environ.get("ROOT_DIR", "/mount"),
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

