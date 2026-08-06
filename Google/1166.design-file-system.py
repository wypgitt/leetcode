#
# @lc app=leetcode id=1166 lang=python3
#
# [1166] Design File System
#
# https://leetcode.com/problems/design-file-system/description/
#
# algorithms
# Medium (65.17%)
# Likes:    645
# Dislikes: 81
# Total Accepted:    92.5K
# Total Submissions: 141.9K
# Testcase Example:  "[\"FileSystem\",\"createPath\",\"get\"]\n[[],[\"/a\",1],[\"/a\"]]"
#
#
# You are asked to design a file system that allows you to create new
# paths and associate them with different values.
#
# The format of a path is one or more concatenated strings of the form: /
# followed by one or more lowercase English letters. For example,
# "/leetcode" and "/leetcode/problems" are valid paths while an empty
# string "" and "/" are not.
#
# Implement the FileSystem class:
#
# bool createPath(string path, int value) Creates a new path and
# associates a value to it if possible and returns true. Returns false if
# the path already exists or its parent path doesn't exist.
#
# int get(string path) Returns the value associated with path or returns
# -1 if the path doesn't exist.
#
# Example 1:
#
# Input:
# ["FileSystem","createPath","get"]
# [[],["/a",1],["/a"]]
# Output:
# [null,true,1]
# Explanation:
# FileSystem fileSystem = new FileSystem();
#
# fileSystem.createPath("/a", 1); // return true
# fileSystem.get("/a"); // return 1
#
# Example 2:
#
# Input:
# ["FileSystem","createPath","createPath","get","createPath","get"]
# [[],["/leet",1],["/leet/code",2],["/leet/code"],["/c/d",1],["/c"]]
# Output:
# [null,true,true,2,false,-1]
# Explanation:
# FileSystem fileSystem = new FileSystem();
#
# fileSystem.createPath("/leet", 1); // return true
# fileSystem.createPath("/leet/code", 2); // return true
# fileSystem.get("/leet/code"); // return 2
# fileSystem.createPath("/c/d", 1); // return false because the parent
# path "/c" doesn't exist.
# fileSystem.get("/c"); // return -1 because this path doesn't exist.
#
# Constraints:
#
# 2 <= path.length <= 100
#
# 1 <= value <= 10^9
#
# Each path is valid and consists of lowercase English letters and '/'.
#
# At most 10^4 calls in total will be made to createPath and get.
#
# @lc code=start
from typing import Dict


class FileSystem:
    def __init__(self):
        """
        Interview explanation:
        Premium. Create path with a value; get value by path. Parent path must
        already exist for createPath. Trie / nested dict of path segments.

        Algorithm:
        - Root dict maps segment → child dict or stores value at key ''.

        Complexity: O(1) init.
        """
        self.root: Dict = {}

    def createPath(self, path: str, value: int) -> bool:
        """
        Interview explanation:
        Create path with value if it does not exist and its parent exists.

        Algorithm:
        - Split path; walk parents; fail if parent missing or path exists;
          create leaf with value.

        Complexity: O(P) for path length in segments.
        """
        parts = [p for p in path.split("/") if p]
        if not parts:
            return False
        node = self.root
        for p in parts[:-1]:
            if p not in node:
                return False
            node = node[p]
            if not isinstance(node, dict):
                return False
        leaf = parts[-1]
        if leaf in node:
            return False
        node[leaf] = {"__val__": value}
        return True

    def get(self, path: str) -> int:
        """
        Interview explanation:
        Return the value stored at path, or -1 if missing.

        Algorithm:
        - Walk segments; return __val__ or -1.

        Complexity: O(P).
        """
        parts = [p for p in path.split("/") if p]
        node = self.root
        for p in parts:
            if p not in node or not isinstance(node[p], dict):
                return -1
            node = node[p]
        return node.get("__val__", -1)
# @lc code=end
