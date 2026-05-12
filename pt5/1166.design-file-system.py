from __future__ import annotations


class FileSystem:
    def __init__(self):
        self.values = {"": -1}

    def createPath(self, path: str, value: int) -> bool:
        if path in self.values:
            return False

        parent = path.rsplit("/", 1)[0]
        if parent not in self.values:
            return False

        self.values[path] = value
        return True

    def get(self, path: str) -> int:
        return self.values.get(path, -1)

