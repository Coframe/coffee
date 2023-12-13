import re
import os
import time
from agents.baseline import BaselineAgent
from agents.component_path import ComponentPathAgent
from file_watcher import FileWatcher
import shutil
import json
from pydantic import BaseModel

CodeAgent = BaselineAgent()
PathAgent = ComponentPathAgent()


class FileContext(BaseModel):
    file_path: str
    file_content: str
    root_directory: str
    mount_dir: str
    working_dir: str


class BrewContext(FileContext):
    brew_path: str
    brew_content: str
    coffee_import_statement: str
    coffee_tag: dict


def process_file(file_path, mount_dir=None, root_directory=None):
    """
    Detects and processes <Coffee> and <Component coffee="..."> tags.
    """
    with open(file_path, "r") as file:
        file_content = file.read()

    ctx = FileContext(
        file_path=file_path,
        file_content=file_content,
        root_directory=root_directory,
        mount_dir=mount_dir,
        working_dir=os.path.join(os.path.dirname(file_path), mount_dir),
    )

    # Extract and process <Coffee> tag
    coffee_tag = extract_tag(file_content, tag="Coffee")
    if coffee_tag:
        print(f"<Coffee> tag found in {file_path}")
        process_coffee_tag(coffee_tag=coffee_tag, ctx=ctx)

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

    brew_path = os.path.join(working_dir, "Brew.tsx")
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
        set_mount("./mount", working_dir, False)
        pour_component(pour_path=pour, ctx=brew_ctx)
    else:
        print("Brewing new component...")
        set_mount("./mount", working_dir, True)
        brew_component(ctx=brew_ctx)

    return


def brew_component(ctx: BrewContext = None):
    file_content, modfied = set_import(
        ctx.file_content, ctx.coffee_import_statement, True
    )
    if modfied:
        with open(ctx.file_path, "w") as file:
            file.write(file_content)

    prompt = ctx.coffee_tag["children"]

    for update in CodeAgent.modify_file(
        source_file=ctx.brew_path,
        user_query=prompt,
        file_content=ctx.brew_content,
        parent_file_content=file_content,
    ):
        print(update)


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
        insert_index = file_content.find("\n", file_content.rfind("import "))
        file_content = (
            file_content[: insert_index + 1]
            + import_statement
            + file_content[insert_index + 1 :]
        )
        modified = True

    return file_content, modified


def set_mount(source, target, mount=True):
    """
    Mount or unmount the source directory to the target directory.
    """
    if mount and not os.path.exists(target):
        os.makedirs(target)
    for item in os.listdir(source):
        s = os.path.join(source, item)
        d = os.path.join(target, item)
        if os.path.isdir(s):
            os.symlink(s, d) if mount else os.remove(d)
        else:
            shutil.copy2(s, d) if mount else os.remove(d)


def parse_config(path):
    """
    Reads and parses config file
    """

    default_config = {"mount": "./components", "patterns": ["**/*.tsx", "**/*.jsx"]}
    try:
        with open(path, "r") as file:
            return dict(default_config, **json.load(file))
    except FileNotFoundError:
        return default_config


watcher = None

if __name__ == "__main__":
    if watcher:
        print("Hot reloading...")
        watcher.stop()

    print("Starting...")
    root_directory = os.environ.get("ROOT_DIR", "/mount")
    config = parse_config(root_directory + "/coffee.config.json")

    watcher = FileWatcher(
        root_directory,
        watch_patterns=config["patterns"],
        ignore_patterns=["Coffee.tsx"],
    )
    watcher.start()
    prev_inc = 0

    while True:
        time.sleep(1)
        if prev_inc != watcher.last_modified_file_inc:
            print(f"File changed: {watcher.last_modified_file}")
            process_file(
                watcher.last_modified_file,
                mount_dir=config["mount"],
                root_directory=root_directory,
            )
            prev_inc = watcher.last_modified_file_inc
