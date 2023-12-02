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
        self._load_ignore_patterns()
        self.observer = Observer()
        self.event_handler = FileSystemEventHandler()
        self.event_handler.on_modified = self._on_modified
        self.thread = Thread(target=self._watch)
        self.last_modified_file = None
        self.last_modified_file_inc = 0


    def _load_ignore_patterns(self):
        # Load ignore patterns from .gitignore files or similar
        patterns_paths = ['/.gitignore']
        for path in patterns_paths:
            try:
                with open(self.base_path + path, 'r') as f:
                   lines = f.readlines()
                   self.ignore_patterns += [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
            except FileNotFoundError:
                continue

        print("Ignore patterns:", self.ignore_patterns)


    def _is_ignored(self, path):
        # Check if the path matches any of the ignore patterns
        relative_path = pathlib.Path(path).relative_to(self.base_path)

        # Check if file or folder is hidden
        if [part for part in relative_path.parts if part.startswith('.') or "brew" in part]:
            return True

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
        if not self._is_ignored(event.src_path):
            self.last_modified_file = event.src_path
            self.last_modified_file_inc += 1

    def _watch(self):
        self.observer.schedule(self.event_handler, self.base_path, recursive=True)
        self.observer.start()
        self.observer.join()

    def start(self):
        self.thread.start()

    def stop(self):
        self.observer.stop()
        self.thread.join()
