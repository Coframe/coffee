import re
import os
import time
from agents.baseline import BaselineAgent
from file_watcher import FileWatcher
import shutil
import json

agent = BaselineAgent()

def process_file(file_path, mount_dir):
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")

    # Extract <Coffee> tag
    coffee = extract_coffee_tag(file_content)

    if not coffee:
        print(f"No <Coffee> tag found in {file_path}")
        return

    brew_path = os.path.join(mount_dir, 'brew', coffee['file'])

    brew_content = ""
    if os.path.exists(brew_path):
        with open(brew_path, 'r') as brew_file:
            brew_content = brew_file.read()

    for update in agent.write_code(user_query=coffee['prompt'], source_file = brew_path, file_content=brew_content, parent_file_content=file_content):
        print(update)

    print('Done at:', brew_path)


def extract_coffee_tag(file_content):
    """
    Looks for <Coffee brew="filename.tsx" ... > Some content </Coffee> tags in the given file content.
    """
    # Regular expression to match the pattern
    pattern = r'<Coffee brew="([^"]+\.tsx)"[^>]*>(.*?)</Coffee>'

    # Find all matches in the file content
    matches = re.findall(pattern, file_content, re.DOTALL)
    if matches:
        # Assuming we want the first match only
        return {'file': matches[0][0], 'prompt': matches[0][1].strip()}
    else:
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

if __name__ == "__main__":
    fe_directory = os.environ.get("FRONTEND_DIR")  # Default to current directory if not set
    config = parse_config(fe_directory+"/coffee.config.json")
    mount_dir = fe_directory+'/'+config['mount']
    mount('./mount', mount_dir)
    # Retrieve the directory to watch from environment variable or set a default
    watcher = FileWatcher(fe_directory, watch_patterns=config['patterns'], ignore_patterns=[config['mount']+"/**/*"])

    watcher.start()
    prev_inc = 0

    while True:
        try:
            time.sleep(1)
            if prev_inc != watcher.last_modified_file_inc:
                print(f"File changed: {watcher.last_modified_file}")
                process_file(watcher.last_modified_file, mount_dir)
                prev_inc = watcher.last_modified_file_inc
        except Exception as e:
            prev_inc = watcher.last_modified_file_inc
            print("An error occurred:")
            print(e)

