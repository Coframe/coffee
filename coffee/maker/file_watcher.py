import os
from threading import Thread
import pathlib
import fnmatch
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileWatcher:
    def __init__(self, base_path, ignore_patterns=None):
        self.base_path = base_path
        self.ignore_patterns = ['.git/*']
        if ignore_patterns:
            self.ignore_patterns.extend(ignore_patterns)
        self._load_ignore_patterns(base_path)
        self.observer = Observer()
        self.event_handler = FileSystemEventHandler()
        self.event_handler.on_modified = self._on_modified
        self.thread = Thread(target=self._watch)
        self.last_modified_file = None
        self.last_modified_file_checked = False

    def _load_ignore_patterns(self, base_path):
        # Find all .gitignore files in the directory tree
        gitignore_paths = [os.path.join(root, '.gitignore')
                           for root, dirs, files in os.walk(base_path)
                           if '.gitignore' in files]

        # Process each .gitignore file
        for path in gitignore_paths:
            try:
                with open(path, 'r') as file:
                    # Extract non-empty, non-comment lines
                    self.ignore_patterns.extend(
                        [line.strip() for line in file if line.strip() and not line.strip().startswith('#')]
                    )
            except FileNotFoundError:
                # Consider logging this error if necessary
                pass

    def _is_ignored(self, path):
        # Check if the path matches any of the ignore patterns
        relative_path = pathlib.Path(path).relative_to(pathlib.Path.cwd())

        for pattern in self.ignore_patterns:
            # Check the full path for a match
            if fnmatch.fnmatch(str(relative_path), pattern):
                return True
            # Check each part of the path for a match
            for part in relative_path.parts:
                if fnmatch.fnmatch(part, pattern.rstrip('/')):
                    return True
        return False

    def _on_modified(self, event):
        if self._is_ignored(event.src_path):
            return
        self.last_modified_file = event.src_path
        self.last_modified_file_checked = False


    def _watch(self):
        self.observer.schedule(self.event_handler, self.base_path, recursive=True)
        self.observer.start()
        self.observer.join()

    def start(self):
        self.thread.start()

    def stop(self):
        self.observer.stop()
        self.thread.join()
