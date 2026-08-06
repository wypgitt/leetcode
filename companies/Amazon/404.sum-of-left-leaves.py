#
# @lc app=leetcode id=404 lang=python3
#
# [404] Sum of Left Leaves
#
# https://leetcode.com/problems/sum-of-left-leaves/description/
#
# algorithms
# Easy (63.0%)
# Likes:    5826
# Dislikes: 329
# Total Accepted:    824K
# Total Submissions: 1.3M
# Testcase Example:  "[3,9,20,null,null,15,7]"
#
# Given the root of a binary tree, return the sum of all left leaves.
#
# A leaf is a node with no children. A left leaf is a leaf that is the left
# child of another node.
#
# Example 1:
#
# Input: root = [3,9,20,null,null,15,7]
# Output: 24
# Explanation: There are two left leaves in the binary tree, with values 9 and
# 15 respectively.
#
# Example 2:
#
# Input: root = [1]
# Output: 0
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 1000].
#
# -1000 <= Node.val <= 1000
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
    def sumOfLeftLeaves(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        DFS: a left leaf is a node reached via a left edge with no children.
        Sum those values while traversing.

        Algorithm:
        - dfs(node, is_left): if leaf and is_left, return val; else sum children.

        Complexity: O(n) time, O(h) space.
        """
        def dfs(node: Optional[TreeNode], is_left: bool) -> int:
            if not node:
                return 0
            if not node.left and not node.right:
                return node.val if is_left else 0
            return dfs(node.left, True) + dfs(node.right, False)

        return dfs(root, False)

    def sumOfLeftLeavesBFS(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        Alternate BFS: queue of (node, is_left); accumulate left leaves.

        Algorithm:
        - Level-order walk; when leaf and is_left, add val.

        Complexity: O(n) time, O(n) space.
        """
        if not root:
            return 0
        from collections import deque
        total = 0
        q = deque([(root, False)])
        while q:
            node, is_left = q.popleft()
            if not node.left and not node.right and is_left:
                total += node.val
            if node.left:
                q.append((node.left, True))
            if node.right:
                q.append((node.right, False))
        return total
# @lc code=end
