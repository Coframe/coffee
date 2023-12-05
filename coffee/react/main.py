import re
import os
import time
from agents.baseline import BaselineAgent
from file_watcher import FileWatcher
import shutil
import json

agent = BaselineAgent()

def process_file(file_path, mount_dir="./components"):
    with open(file_path, 'r') as file:
        file_content = file.read()


    # Extract <Coffee> tag
    coffee_tag = extract_coffee_tag(file_content)
    if not coffee_tag:
        print(f"No <Coffee> tag found in {file_path}")
        return

    # Mount Coffee
    working_dir = os.path.join(os.path.dirname(file_path), mount_dir)
    coffee_import_statement = f"import Coffee from '{mount_dir}/Coffee'\n"
    mount('./mount', working_dir)
    file_content, modfied = update_imports(file_content, coffee_import_statement, upsert=True)
    if modfied:
        with open(file_path, 'w') as file:
            file.write(file_content)

    brew_file_name = coffee_tag['props']['brew']
    prompt = coffee_tag['children']
    save = coffee_tag['props'].get('pour', False)
    brew_path = os.path.join(working_dir, brew_file_name)
    if save:
        replace_coffee_tag_with_brew(file_path, file_content, coffee_tag, mount_dir=mount_dir, coffee_import_statement=coffee_import_statement)
        umount('./mount', working_dir)
    else:
        brew_content = ""
        if os.path.exists(brew_path):
            with open(brew_path, 'r') as brew_file:
                brew_content = brew_file.read()

        for update in agent.write_code(user_query=prompt, source_file = brew_path, file_content=brew_content, parent_file_content=file_content):
            print(update)


    print('Done at:', brew_path)

def replace_coffee_tag_with_brew(file_path, file_content, coffee_tag, attributes_to_remove=['brew', 'pour'], mount_dir=None, coffee_import_statement=None):
    """
    Replaces the <Coffee> tag with <BrewedComponent>.
    1. Replace <Coffee ...> </Coffee> tag with <ComponentName ...props />
    2. Append import ComponentName from './coffee/brew/ComponentName' after the last import statement.
    """
    print(f'Replacing <Coffee> with {file_path} component...')

    # Extracting component name and tag positions
    component_name = coffee_tag['props']['brew'].split('.')[0]
    coffee_start, coffee_end = coffee_tag['match'].span()
    attributes = coffee_tag["attributes"]
    for attr in attributes_to_remove:
        attributes = re.sub(rf'\b{attr}="[^"]+"\s*|\b{attr}\b\s*', '', attributes)
    file_content = file_content[:coffee_start] + f'<{component_name} {attributes.strip()} />' + file_content[coffee_end:]

    # Add import statement
    import_statement = f"import {component_name} from '{mount_dir}/{component_name}'\n"
    file_content, _ = update_imports(file_content, import_statement, upsert=True)
    file_content, _ = update_imports(file_content, coffee_import_statement, remove=True)

    # Write the modified content back to the file
    with open(file_path, 'w') as file:
        file.write(file_content)

    print("Replacement complete.")

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


def extract_coffee_tag(file_content):
    """
    Extracts the first <Coffee ... > ... </Coffee>  or <Coffee .../> tag from the given file content.
    Returns the match object, props, and children.
    """
    pattern = r'<Coffee([^>/]*)(?:>(.*?)</Coffee>|/>)'
    match = re.search(pattern, file_content, re.DOTALL)

    if match:
        attributes, content = match.groups()
        props = {m[0]: m[1] or True for m in re.findall(r'(\w+)(?:=["\']([^"\']+)["\']|\b)', attributes)}
        return {'match': match, 'props': props, 'children': content.strip() if content else "", 'attributes': attributes}

    return None

def parse_config(path):
    """Read and parse json file at path"""
    with open(path, 'r') as file:
        return json.load(file)

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

if __name__ == "__main__":
    fe_directory = os.environ.get("FRONTEND_DIR")  # Default to current directory if not set
    config = parse_config(fe_directory+"/coffee.config.json")

    # Retrieve the directory to watch from environment variable or set a default
    watcher = FileWatcher(fe_directory, watch_patterns=config['patterns'], ignore_patterns=["Coffee.tsx"])

    watcher.start()
    prev_inc = 0

    while True:
        time.sleep(1)
        if prev_inc != watcher.last_modified_file_inc:
            print(f"File changed: {watcher.last_modified_file}")
            process_file(watcher.last_modified_file, mount_dir=config['mount'])
            prev_inc = watcher.last_modified_file_inc


