#
# @lc app=leetcode id=549 lang=python3
#
# [549] Binary Tree Longest Consecutive Sequence II
#
# https://leetcode.com/problems/binary-tree-longest-consecutive-sequence-ii/description/
#
# algorithms
# Medium (50.17%)
# Likes:    1206
# Dislikes: 108
# Total Accepted:    63.7K
# Total Submissions: 127K
# Testcase Example:  "[1,2,3]"
#
#
# Given the root of a binary tree, return the length of the longest
# consecutive path in the tree.
#
# A consecutive path is a path where the values of the consecutive nodes
# in the path differ by one. This path can be either increasing or
# decreasing.
#
# For example, [1,2,3,4] and [4,3,2,1] are both considered valid, but the
# path [1,2,4,3] is not valid.
#
# On the other hand, the path can be in the child-Parent-child order,
# where not necessarily be parent-child order.
#
# Example 1:
#
# Input: root = [1,2,3]
# Output: 2
# Explanation: The longest consecutive path is [1, 2] or [2, 1].
#
# Example 2:
#
# Input: root = [2,1,3]
# Output: 3
# Explanation: The longest consecutive path is [1, 2, 3] or [3, 2, 1].
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 3 * 10^4].
#
# -3 * 10^4 <= Node.val <= 3 * 10^4
#
# @lc code=start
from typing import Optional, Tuple
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
        Path may go child → parent → other child and increase or decrease by 1.
        For each node return (inc, dec): longest increasing / decreasing streak
        starting at this node going downward; combine with children for paths
        through the node.

        Algorithm:
        - dfs returns (inc, dec) lengths including the node.
        - If child.val == node.val+1, extend inc; if child.val == node.val-1, extend dec.
        - Path length through node = inc + dec - 1; track global max.

        Complexity: O(n) time, O(h) space.
        """
        self.ans = 0

        def dfs(node: Optional[TreeNode]) -> Tuple[int, int]:
            if not node:
                return 0, 0
            inc = dec = 1
            for child in (node.left, node.right):
                if not child:
                    continue
                c_inc, c_dec = dfs(child)
                if child.val == node.val + 1:
                    inc = max(inc, c_inc + 1)
                if child.val == node.val - 1:
                    dec = max(dec, c_dec + 1)
            self.ans = max(self.ans, inc + dec - 1)
            return inc, dec

        dfs(root)
        return self.ans
# @lc code=end

