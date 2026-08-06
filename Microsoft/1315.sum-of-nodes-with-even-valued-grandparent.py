#
# @lc app=leetcode id=1315 lang=python3
#
# [1315] Sum of Nodes with Even-Valued Grandparent
#
# https://leetcode.com/problems/sum-of-nodes-with-even-valued-grandparent/description/
#
# algorithms
# Medium (85.97%)
# Likes:    2844
# Dislikes: 79
# Total Accepted:    189K
# Total Submissions: 219K
# Testcase Example:  "[6,7,8,2,7,1,3,9,null,1,4,null,null,null,5]"
#
# Given the root of a binary tree, return the sum of values of nodes with an
# even-valued grandparent. If there are no nodes with an even-valued
# grandparent, return 0.
#
# A grandparent of a node is the parent of its parent if it exists.
#
# Example 1:
#
# Input: root = [6,7,8,2,7,1,3,9,null,1,4,null,null,null,5]
# Output: 18
# Explanation: The red nodes are the nodes with even-value grandparent while
# the blue nodes are the even-value grandparents.
#
# Example 2:
#
# Input: root = [1]
# Output: 0
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^4].
#
# 1 <= Node.val <= 100
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
    def sumEvenGrandparent(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        Sum node values whose grandparent is even. DFS carrying (parent, grandparent)
        values (or None).

        Algorithm:
        - dfs(node, parent, gp): if gp even add node.val; recurse with updated lineage.

        Complexity: O(n) time, O(h) space.
        """
        ans = 0

        def dfs(node, parent, gp):
            nonlocal ans
            if not node:
                return
            if gp is not None and gp % 2 == 0:
                ans += node.val
            dfs(node.left, node.val, parent)
            dfs(node.right, node.val, parent)

        dfs(root, None, None)
        return ans
# @lc code=end

