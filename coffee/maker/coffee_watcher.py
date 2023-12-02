import re
import os
import time
from models.baseline_tiny import BaselineTinyAI
from services.file_watcher import FileWatcher

agent = BaselineTinyAI()

def process_file(file_path):
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

    brew_path = os.path.join(os.path.dirname(file_path), 'brew', coffee['file'])

    brew_content = ""
    if os.path.exists(brew_path):
        with open(brew_path, 'r') as brew_file:
            brew_content = brew_file.read()

    for update in agent.write_code(user_query=coffee['prompt'], source_file = brew_path, file_content=brew_content, parent_file_content=file_content):
        pass

    print('Done.')


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


if __name__ == "__main__":
    try:
        # Retrieve the directory to watch from environment variable or set a default
        watch_directory = os.environ.get("FRONTEND_DIR", ".")  # Default to current directory if not set
        watcher = FileWatcher(watch_directory)

        watcher.start()
        prev_inc = 0

        while True:
            time.sleep(1)
            if prev_inc != watcher.last_modified_file_inc:
                print(f"File changed: {watcher.last_modified_file}")
                process_file(watcher.last_modified_file)
                prev_inc = watcher.last_modified_file_inc

    except Exception as e:
        print("An error occurred and the application is closing")
        print(e)
        watcher.stop() if 'watcher' in locals() else None  # Safely attempt to stop the watcher if it was initialized
