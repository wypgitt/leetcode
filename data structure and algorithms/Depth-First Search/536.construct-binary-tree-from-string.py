#
# @lc app=leetcode id=536 lang=python3
#
# [536] Construct Binary Tree from String
#
# https://leetcode.com/problems/construct-binary-tree-from-string/description/
#
# algorithms
# Medium (58.70%)
# Likes:    1135
# Dislikes: 184
# Total Accepted:    127.5K
# Total Submissions: 217.3K
# Testcase Example:  "\"4(2(3)(1))(6(5))\""
#
#
# You need to construct a binary tree from a string consisting of
# parenthesis and integers.
#
# The whole input represents a binary tree. It contains an integer
# followed by zero, one or two pairs of parenthesis. The integer
# represents the root's value and a pair of parenthesis contains a child
# binary tree with the same structure.
#
# You always start to construct the left child node of the parent first if
# it exists.
#
# Example 1:
#
# Input: s = "4(2(3)(1))(6(5))"
# Output: [4,2,6,3,1,5]
#
# Example 2:
#
# Input: s = "4(2(3)(1))(6(5)(7))"
# Output: [4,2,6,3,1,5,7]
#
# Example 3:
#
# Input: s = "-4(2(3)(1))(6(5)(7))"
# Output: [-4,2,6,3,1,5,7]
#
# Constraints:
#
# 0 <= s.length <= 3 * 10^4
#
# s consists of digits, '(', ')', and '-' only.
#
# All numbers in the tree have value at most than 2^30.
#
# @lc code=start
from typing import Optional
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def str2tree(self, s: str) -> Optional[TreeNode]:
        """
        Interview explanation:
        Parse "val(left)(right)" recursively: read an optional signed integer,
        then if '(' follows, parse left subtree, then optional right subtree,
        each closed by ')'.

        Algorithm:
        - Index-driven recursive parse.
        - Read number; if next char '(', recurse for left; if another '(', right.

        Complexity: O(n) time, O(h) recursion space.
        """
        if not s:
            return None
        self.i = 0
        n = len(s)

        def parse() -> Optional[TreeNode]:
            if self.i >= n:
                return None
            sign = 1
            if s[self.i] == "-":
                sign = -1
                self.i += 1
            val = 0
            while self.i < n and s[self.i].isdigit():
                val = val * 10 + int(s[self.i])
                self.i += 1
            node = TreeNode(sign * val)
            if self.i < n and s[self.i] == "(":
                self.i += 1  # '('
                node.left = parse()
                self.i += 1  # ')'
            if self.i < n and s[self.i] == "(":
                self.i += 1
                node.right = parse()
                self.i += 1
            return node

        return parse()
# @lc code=end

