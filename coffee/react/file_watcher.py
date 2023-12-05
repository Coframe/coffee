from threading import Thread
import pathlib
import fnmatch
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FileWatcher:
    def __init__(self, base_path, watch_patterns = None, ignore_patterns=None):
        self.base_path = base_path
        self.watch_patterns = watch_patterns
        self.ignore_patterns = ignore_patterns+['.git/*']
        if ignore_patterns:
            self.ignore_patterns.extend(ignore_patterns)
        self._load_ignore_patterns()

        if(self.watch_patterns):
            print("Watch patterns:", self.watch_patterns)
        else:
            print("Ignore patterns:", self.ignore_patterns)

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


    def _is_ignored(self, path):
        relative_path = pathlib.Path(path).relative_to(self.base_path)

        for pattern in self.ignore_patterns:
            # Check the full path for a match
            if fnmatch.fnmatch(str(relative_path), pattern):
                return True
            # Check each part of the path for a match
            for part in relative_path.parts:
                if fnmatch.fnmatch(part, pattern.rstrip('/')):
                    return True

        # Check if any watch patterns are matched:
        if self.watch_patterns:
            for pattern in self.watch_patterns:
                # Check the full path for a match
                if fnmatch.fnmatch(str(relative_path), pattern):
                    return False
                # Check each part of the path for a match
                for part in relative_path.parts:
                    if fnmatch.fnmatch(part, pattern.rstrip('/')):
                        return False
            return True

        return False

    def _on_modified(self, event):
        if not self._is_ignored(event.src_path):
            print("Modified:", event.src_path)
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
