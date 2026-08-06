#
# @lc app=leetcode id=1457 lang=python3
#
# [1457] Pseudo-Palindromic Paths in a Binary Tree
#
# https://leetcode.com/problems/pseudo-palindromic-paths-in-a-binary-tree/description/
#
# algorithms
# Medium (68.39%)
# Likes:    3356
# Dislikes: 131
# Total Accepted:    239K
# Total Submissions: 350K
# Testcase Example:  "[2,3,1,3,1,null,1]"
#
# Given a binary tree where node values are digits from 1 to 9. A path in the
# binary tree is said to be pseudo-palindromic if at least one permutation of
# the node values in the path is a palindrome.
#
# Return the number of pseudo-palindromic paths going from the root node to
# leaf nodes.
#
# Example 1:
#
# Input: root = [2,3,1,3,1,null,1]
# Output: 2
# Explanation: The figure above represents the given binary tree. There are
# three paths going from the root node to leaf nodes: the red path [2,3,3], the
# green path [2,1,1], and the path [2,3,1]. Among these paths only red path and
# green path are pseudo-palindromic paths since the red path [2,3,3] can be
# rearranged in [3,2,3] (palindrome) and the green path [2,1,1] can be
# rearranged in [1,2,1] (palindrome).
#
# Example 2:
#
# Input: root = [2,1,1,1,3,null,null,null,null,null,1]
# Output: 1
# Explanation: The figure above represents the given binary tree. There are
# three paths going from the root node to leaf nodes: the green path [2,1,1],
# the path [2,1,3,1], and the path [2,1]. Among these paths only the green path
# is pseudo-palindromic since [2,1,1] can be rearranged in [1,2,1]
# (palindrome).
#
# Example 3:
#
# Input: root = [9]
# Output: 1
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^5].
#
# 1 <= Node.val <= 9
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
    def pseudoPalindromicPaths(self, root: Optional["TreeNode"]) -> int:
        """
        Interview explanation:
        Count root-to-leaf paths whose digit frequencies can form a palindrome
        (at most one odd count). Use DFS with a bitmask of parity of counts
        for digits 1..9.

        Algorithm:
        - DFS with mask ^= 1<<val; at leaf, path ok if mask is power of two
          (mask & (mask-1) == 0).

        Complexity: O(n) time, O(h) space.
        """
        self.ans = 0

        def dfs(node, mask):
            if not node:
                return
            mask ^= 1 << node.val
            if not node.left and not node.right:
                if mask & (mask - 1) == 0:
                    self.ans += 1
                return
            dfs(node.left, mask)
            dfs(node.right, mask)

        dfs(root, 0)
        return self.ans

    def pseudoPalindromicPaths_counter(self, root: Optional["TreeNode"]) -> int:
        """
        Interview explanation:
        Alternate: maintain frequency array/Counter along the path; at leaf
        count odds <= 1.

        Algorithm:
        - DFS with freq[10]; increment/decrement on enter/exit; check at leaves.

        Complexity: O(n) time, O(h) space.
        """
        freq = [0] * 10
        self.ans = 0

        def dfs(node):
            if not node:
                return
            freq[node.val] += 1
            if not node.left and not node.right:
                if sum(f % 2 for f in freq) <= 1:
                    self.ans += 1
            else:
                dfs(node.left)
                dfs(node.right)
            freq[node.val] -= 1

        dfs(root)
        return self.ans
# @lc code=end
