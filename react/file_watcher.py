from threading import Thread
import pathlib
import fnmatch
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import igittigitt
from itertools import islice


class FileWatcher:
    def __init__(self, base_path, watch_patterns=None, ignore_patterns=None):
        self.base_path = base_path
        print("Watching directory:")
        display_content(self.base_path)
        self.watch_patterns = watch_patterns
        self.ignore_patterns = ignore_patterns + [".git/*"]
        if ignore_patterns:
            self.ignore_patterns.extend(ignore_patterns)

        gitignore_path = pathlib.Path(self.base_path) / ".gitignore"
        if gitignore_path.exists():
            self.gitignore = igittigitt.IgnoreParser()
            self.gitignore.parse_rule_file(gitignore_path)
        else:
            self.gitignore = None  # Set to None if no .gitignore file exists
          
        if self.watch_patterns:
            print("Watch patterns:", self.watch_patterns)
        else:
            print("Ignore patterns:", self.ignore_patterns)

        self.observer = Observer()
        self.event_handler = FileSystemEventHandler()
        self.event_handler.on_modified = self._on_modified
        self.thread = Thread(target=self._watch)
        self.last_modified_file = None
        self.last_modified_file_inc = 0

    def _is_ignored(self, path):
        relative_path = pathlib.Path(path).relative_to(self.base_path)

        if self.gitignore and self.gitignore.match(pathlib.Path(path)):
            return True

        for pattern in self.ignore_patterns:
            # Check the full path for a match
            if fnmatch.fnmatch(str(relative_path), pattern):
                return True
            # Check each part of the path for a match
            for part in relative_path.parts:
                if fnmatch.fnmatch(part, pattern.rstrip("/")):
                    return True

        # Check if any watch patterns are matched:
        if self.watch_patterns:
            for pattern in self.watch_patterns:
                # Check the full path for a match
                if fnmatch.fnmatch(str(relative_path), pattern):
                    return False
                # Check each part of the path for a match
                for part in relative_path.parts:
                    if fnmatch.fnmatch(part, pattern.rstrip("/")):
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


def display_content(dir_path, n=10):
    folders_and_files = sorted(
        pathlib.Path(dir_path).iterdir(), key=lambda p: (not p.is_dir(), p.name)
    )
    if len(folders_and_files) == 0:
        raise Exception("No files found in the path")
    for path in islice(folders_and_files, n):
        print(f"  {['📄', '📁'][+path.is_dir()]} {path.relative_to(dir_path)}")
    if len(folders_and_files) > n:
        print("  ...")
