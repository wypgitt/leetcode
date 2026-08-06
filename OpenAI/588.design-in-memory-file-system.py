#
# @lc app=leetcode id=588 lang=python3
#
# [588] Design In-Memory File System
#
# https://leetcode.com/problems/design-in-memory-file-system/description/
#
# algorithms
# Hard (48.30%)
# Likes:    1586
# Dislikes: 176
# Total Accepted:    144.5K
# Total Submissions: 299.1K
# Testcase Example:  "[\"FileSystem\",\"ls\",\"mkdir\",\"addContentToFile\",\"ls\",\"readContentFromFile\"]\n[[],[\"/\"],[\"/a/b/c\"],[\"/a/b/c/d\",\"hello\"],[\"/\"],[\"/a/b/c/d\"]]"
#
#
# Design a data structure that simulates an in-memory file system.
#
# Implement the FileSystem class:
#
# FileSystem() Initializes the object of the system.
#
# List<String> ls(String path)
#
# If path is a file path, returns a list that only contains this file's
# name.
#
# If path is a directory path, returns the list of file and directory
# names in this directory.
#
#         The answer should in lexicographic order.
#
# void mkdir(String path) Makes a new directory according to the given
# path. The given directory path does not exist. If the middle directories
# in the path do not exist, you should create them as well.
#
# void addContentToFile(String filePath, String content)
#
# If filePath does not exist, creates that file containing given content.
#
# If filePath already exists, appends the given content to original
# content.
#
# String readContentFromFile(String filePath) Returns the content in the
# file at filePath.
#
# Example 1:
#
# Input
# ["FileSystem", "ls", "mkdir", "addContentToFile", "ls",
# "readContentFromFile"]
# [[], ["/"], ["/a/b/c"], ["/a/b/c/d", "hello"], ["/"], ["/a/b/c/d"]]
# Output
# [null, [], null, null, ["a"], "hello"]
#
# Explanation
# FileSystem fileSystem = new FileSystem();
# fileSystem.ls("/");                         // return []
# fileSystem.mkdir("/a/b/c");
# fileSystem.addContentToFile("/a/b/c/d", "hello");
# fileSystem.ls("/");                         // return ["a"]
# fileSystem.readContentFromFile("/a/b/c/d"); // return "hello"
#
# Constraints:
#
# 1 <= path.length, filePath.length <= 100
#
# path and filePath are absolute paths which begin with '/' and do not end
# with '/' except that the path is just "/".
#
# You can assume that all directory names and file names only contain
# lowercase letters, and the same names will not exist in the same
# directory.
#
# You can assume that all operations will be passed valid parameters, and
# users will not attempt to retrieve file content or list a directory or
# file that does not exist.
#
# You can assume that the parent directory for the file in
# addContentToFile will exist.
#
# 1 <= content.length <= 50
#
# At most 300 calls will be made to ls, mkdir, addContentToFile, and
# readContentFromFile.
#
# @lc code=start
from typing import Dict, List, Optional


class _Node:
    __slots__ = ("children", "content", "is_file")

    def __init__(self) -> None:
        self.children: Dict[str, "_Node"] = {}
        self.content: str = ""
        self.is_file: bool = False


class FileSystem:
    def __init__(self):
        """
        Interview explanation:
        Trie of path segments: directories hold children; files hold content.
        All public ops walk/create nodes along split path parts.

        Algorithm:
        - Root is an empty directory node.
        - Paths split on '/' (ignore empties from leading/trailing slashes).

        Complexity: O(1) init; structure grows with created paths.
        """
        self.root = _Node()

    def _traverse(self, path: str, create: bool = False) -> Optional[_Node]:
        node = self.root
        if path == "/":
            return node
        for part in path.split("/"):
            if not part:
                continue
            if part not in node.children:
                if not create:
                    return None
                node.children[part] = _Node()
            node = node.children[part]
        return node

    def ls(self, path: str) -> List[str]:
        """
        Interview explanation:
        If path is a file, return a one-element list with its name; if a
        directory, return sorted names of its direct children.

        Algorithm:
        - Walk to the node for path.
        - File → [basename]; directory → sorted(children.keys()).

        Complexity: O(P + C log C) for path length P and C children.
        """
        node = self._traverse(path)
        assert node is not None
        if node.is_file:
            return [path.rstrip("/").split("/")[-1]]
        return sorted(node.children.keys())

    def mkdir(self, path: str) -> None:
        """
        Interview explanation:
        Create the directory and all missing intermediate directories along path.

        Algorithm:
        - Traverse with create=True so each missing segment becomes a dir node.

        Complexity: O(P) time for path length P.
        """
        self._traverse(path, create=True)

    def addContentToFile(self, filePath: str, content: str) -> None:
        """
        Interview explanation:
        Create the file (and parents) if needed, then append content string.

        Algorithm:
        - Traverse/create to filePath; mark is_file; content += content.

        Complexity: O(P + |content|) time.
        """
        node = self._traverse(filePath, create=True)
        assert node is not None
        node.is_file = True
        node.content += content

    def readContentFromFile(self, filePath: str) -> str:
        """
        Interview explanation:
        Return the full string content stored at the file path.

        Algorithm:
        - Traverse to filePath; return node.content.

        Complexity: O(P) time to walk; result string is the stored content.
        """
        node = self._traverse(filePath)
        assert node is not None
        return node.content
# @lc code=end

