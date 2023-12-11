import re
import os
import time
from agents.baseline import BaselineAgent
from agents.component_path import ComponentPathAgent
from file_watcher import FileWatcher
import shutil
import json

CodeAgent = BaselineAgent()
PathAgent = ComponentPathAgent()

def process_file(file_path, mount_dir="./components", fe_directory=None):
    with open(file_path, 'r') as file:
        file_content = file.read()

    # Extract <Coffee> tag
    coffee_tag = extract_coffee_tag(file_content)
    if coffee_tag:
        print(f"<Coffee> tag found in {file_path}")
        working_dir = os.path.join(os.path.dirname(file_path), mount_dir)
        mount('./mount', working_dir)
        process_coffee_tag(file_path, working_dir=working_dir, file_content=file_content, coffee_tag=coffee_tag, mount_dir=mount_dir)
        return

    # Extract components with <Component coffee="...">
    caffeinated_component = extract_caffeinated_component(file_content)
    if caffeinated_component:
        print(f"Caffeinated component found in {file_path}")
        proccess_caffeinated_component(file_path, file_content=file_content, caffeinated_component=caffeinated_component, fe_directory=fe_directory)
        return

    print('Done')

def process_coffee_tag(file_path, working_dir, file_content, coffee_tag, mount_dir):
    coffee_import_statement = f"import Coffee from '{mount_dir}/Coffee'\n"
    file_content, modfied = update_imports(file_content, coffee_import_statement, upsert=True)
    if modfied:
        with open(file_path, 'w') as file:
            file.write(file_content)

    brew_path = os.path.join(working_dir, '__brew__.tsx')
    brew_content = ""
    if os.path.exists(brew_path):
        with open(brew_path, 'r') as brew_file:
            brew_content = brew_file.read()

    prompt = coffee_tag['children']
    pour_path = coffee_tag['props'].get('pour', None)

    if pour_path:
        print('Pouring to', pour_path)
        replace_coffee_tag_with_component(file_path, file_content, coffee_tag, pour_path=pour_path, mount_dir=mount_dir, coffee_import_statement=coffee_import_statement, brew_content=brew_content)
        umount('./mount', working_dir)
    else:
        print('Brewing new component...')
        for update in CodeAgent.modify_file(source_file = brew_path, user_query=prompt, file_content=brew_content, parent_file_content=file_content):
            print(update)

def replace_coffee_tag_with_component(file_path, file_content, coffee_tag, pour_path=None, attributes_to_remove=['brew', 'pour'], mount_dir=None, coffee_import_statement=None, brew_content=None):
    """
    Replaces the <Coffee> tag with <BrewedComponent>.
    1. Replace <Coffee ...> </Coffee> tag with <ComponentName ...props />
    2. Append import ComponentName from './coffee/brew/ComponentName' after the last import statement.
    """
    print(f'Replacing <Coffee> with {file_path} component...')

    # Update tag
    component_name = pour_path.split('.')[0]
    coffee_start, coffee_end = coffee_tag['match'].span()
    attributes = coffee_tag["attributes"]
    for attr in attributes_to_remove:
        attributes = re.sub(rf'\b{attr}="[^"]+"\s*|\b{attr}\b\s*', '', attributes)
    file_content = file_content[:coffee_start] + f'<{component_name} {attributes.strip()} />' + file_content[coffee_end:]

    # Update import statements
    import_statement = f"import {component_name} from '{mount_dir}/{component_name}'\n"
    file_content, _ = update_imports(file_content, import_statement, upsert=True)
    file_content, _ = update_imports(file_content, coffee_import_statement, remove=True)

    # Create component file
    component_file_path = os.path.join(os.path.dirname(file_path), mount_dir, pour_path)
    with open(component_file_path, 'w') as component_file:
        component_file.write(brew_content)

    with open(file_path, 'w') as file:
        file.write(file_content)

    print("Replacement complete.")

def proccess_caffeinated_component(file_path, file_content, caffeinated_component, fe_directory):
    component_name = caffeinated_component['match'].group(1)

    import_pattern = rf"({component_name})(.*?)from\s[\'\"](.*?)[\'\"]"
    match = re.search(import_pattern, file_content, re.DOTALL)

    if not match:
        print(f"Could not find import statement for {component_name}")
        return

    # TODO: move to watcher:
    command = f"find {fe_directory} -type f \\( -name \"*.tsx\" -o -name \"*.jsx\" \\) -not -path \"*/node_modules/*\""
    directory_structure = os.popen(command).read()
    component_file_path = None
    for update in PathAgent.run(
        component=component_name,
        parent_file_path=file_path,
        import_statement=match.group(0),
        directory_structure=directory_structure):
        print(update)
        if isinstance(update, dict) and update.get('file_path'):
            component_file_path = update['file_path']

    if not component_file_path:
        print(f"Could not find component file for {component_name}")
        return

    with open(component_file_path, 'r') as component_file:
        component_file_content = component_file.read()
        if not component_file_content:
            # TODO: handle back-and-forth with agent if file content is not found
            print(f"Could not read component file for {component_name} at {component_file_path}")
            return

    for update in CodeAgent.modify_file(
        user_query= caffeinated_component['props']['coffee'],
        source_file = component_file_path,
        file_content=component_file_content,
        parent_file_content=file_content):
        print(update)

def extract_coffee_tag(file_content):
    """
    Extracts the first <Coffee ... > ... </Coffee>  or <Coffee .../> tag from the given file content.
    Returns the match object, props, and children.
    """
    pattern = r'<Coffee\s?([^>/]*)(?:>(.*?)</Coffee>|/>)'
    match = re.search(pattern, file_content, re.DOTALL)

    if match:
        attributes, content = match.groups()
        props = {m[0]: m[1] or True for m in re.findall(r'(\w+)(?:=["\']([^"\']+)["\']|\b)', attributes)}
        return {'match': match, 'props': props, 'children': content.strip() if content else "", 'attributes': attributes}

    return None

def extract_caffeinated_component(file_content):
    """
    Extracts the first <MyComponent coffee="..."> tag from the given file content.
    """
    pattern = r'<(\w+)\s([^>/]*)(?:>(.*?)</\1>|/>)'
    match = re.search(pattern, file_content, re.DOTALL)
    if match:
        tag_name, attributes, content = match.groups()
        if 'coffee' in attributes:
            props = {m[0]: m[1] or True for m in re.findall(r'(\w+)(?:=["\']([^"\']+)["\']|\b)', attributes)}
            return {'match': match, 'props': props, 'children': content.strip() if content else "", 'attributes': attributes}

    return None

def update_imports(file_content, import_statement, upsert=False, remove=False):
    """
    Updates the import statements in file_content with the given import_statement.
    """
    import_index = file_content.find(import_statement)
    modified = False

    if(remove and import_index != -1):
        file_content = file_content[:import_index] + file_content[import_index + len(import_statement):]
        modified = True
    if(upsert and import_index == -1):
        insert_index = file_content.find('\n', file_content.rfind('import '))
        file_content = file_content[:insert_index + 1] + import_statement + file_content[insert_index + 1:]
        modified = True

    return file_content, modified

def parse_config(path):
    """Read and parse json file at path."""
    default_config = {
        "mount": "./components",
        "patterns": ['**/*.tsx', '**/*.jsx']
    }
    try:
        with open(path, 'r') as file:
            return dict(default_config, **json.load(file))
    except FileNotFoundError:
        return default_config

def mount(source, target):
    """
    Copy all files from source to target
    """
    if not os.path.exists(target):
        os.makedirs(target)
    for item in os.listdir(source):
        s = os.path.join(source, item)
        d = os.path.join(target, item)
        if os.path.isdir(s):
            print(f"Copying directory {s} to {d}")
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            print(f"Copying file {s} to {d}")
            shutil.copy2(s, d)

def umount(source, target):
    """
    Delete all files from target that are in source
    """
    for item in os.listdir(source):
        s = os.path.join(source, item)
        d = os.path.join(target, item)
        if os.path.isdir(s):
            print(f"Deleting directory {d}")
            shutil.rmtree(d)
        else:
            print(f"Deleting file {d}")
            os.remove(d)

watcher = None

if __name__ == "__main__":
    if(watcher):
        print('Hot reloading...')
        watcher.stop()

    print('Starting...')
    fe_directory = os.environ.get("FRONTEND_DIR", "/frontend_dir")
    config = parse_config(fe_directory+"/coffee.config.json")

    watcher = FileWatcher(fe_directory, watch_patterns=config['patterns'], ignore_patterns=["Coffee.tsx"])

    watcher.start()
    prev_inc = 0

    while True:
        time.sleep(1)
        if prev_inc != watcher.last_modified_file_inc:
            print(f"File changed: {watcher.last_modified_file}")
            process_file(watcher.last_modified_file, mount_dir=config['mount'], fe_directory=fe_directory)
            prev_inc = watcher.last_modified_file_inc


