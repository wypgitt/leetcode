#
# @lc app=leetcode id=298 lang=python3
#
# [298] Binary Tree Longest Consecutive Sequence
#
# https://leetcode.com/problems/binary-tree-longest-consecutive-sequence/description/
#
# algorithms
# Medium (54.84%)
# Likes:    1186
# Dislikes: 239
# Total Accepted:    167.1K
# Total Submissions: 304.8K
# Testcase Example:  "[1,null,3,2,4,null,null,null,5]"
#
#
# Given the root of a binary tree, return the length of the longest
# consecutive sequence path.
#
# A consecutive sequence path is a path where the values increase by one
# along the path.
#
# Note that the path can start at any node in the tree, and you cannot go
# from a node to its parent in the path.
#
# Example 1:
#
# Input: root = [1,null,3,2,4,null,null,null,5]
# Output: 3
# Explanation: Longest consecutive sequence path is 3-4-5, so return 3.
#
# Example 2:
#
# Input: root = [2,null,3,2,null,1]
# Output: 2
# Explanation: Longest consecutive sequence path is 2-3, not 3-2-1, so
# return 2.
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 3 * 10^4].
#
# -3 * 10^4 <= Node.val <= 3 * 10^4
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
    def longestConsecutive(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        Longest parent→child path where values increase by exactly 1.
        DFS carrying the current streak ending at the parent.

        Algorithm:
        - dfs(node, parent_val, length): if node.val == parent_val+1 continue
          streak else reset to 1; update global max; recurse children.

        Complexity: O(n) time, O(h) space.
        """
        self.best = 0

        def dfs(node: Optional[TreeNode], parent_val: int, length: int) -> None:
            if not node:
                return
            length = length + 1 if node.val == parent_val + 1 else 1
            self.best = max(self.best, length)
            dfs(node.left, node.val, length)
            dfs(node.right, node.val, length)

        dfs(root, float("-inf"), 0)
        return self.best
# @lc code=end

