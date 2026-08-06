#
# @lc app=leetcode id=979 lang=python3
#
# [979] Distribute Coins in Binary Tree
#
# https://leetcode.com/problems/distribute-coins-in-binary-tree/description/
#
# algorithms
# Medium (77.32%)
# Likes:    6117
# Dislikes: 251
# Total Accepted:    230K
# Total Submissions: 298K
# Testcase Example:  "[3,0,0]"
#
# You are given the root of a binary tree with n nodes where each node in the
# tree has node.val coins. There are n coins in total throughout the whole
# tree.
#
# In one move, we may choose two adjacent nodes and move one coin from one node
# to another. A move may be from parent to child, or from child to parent.
#
# Return the minimum number of moves required to make every node have exactly
# one coin.
#
# Example 1:
#
# Input: root = [3,0,0]
# Output: 2
# Explanation: From the root of the tree, we move one coin to its left child,
# and one coin to its right child.
#
# Example 2:
#
# Input: root = [0,3,0]
# Output: 3
# Explanation: From the left child of the root, we move two coins to the root
# [taking two moves]. Then, we move one coin from the root of the tree to the
# right child.
#
# Constraints:
#
# The number of nodes in the tree is n.
#
# 1 <= n <= 100
#
# 0 <= Node.val <= n
#
# The sum of all Node.val is n.
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
    def distributeCoins(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        Excess at a subtree = (total coins) - (number of nodes). That excess
        must cross the edge to the parent, so |excess| moves are required on
        that edge. Sum |excess| over all nodes (post-order).

        Algorithm:
        - dfs(node) returns excess = coins_in_subtree - nodes_in_subtree.
        - After left/right: excess = node.val - 1 + L + R; ans += |L| + |R|.
        - Return ans.

        Complexity: O(n) time, O(h) space.
        """
        ans = 0

        def dfs(node: Optional[TreeNode]) -> int:
            nonlocal ans
            if not node:
                return 0
            left = dfs(node.left)
            right = dfs(node.right)
            ans += abs(left) + abs(right)
            return node.val - 1 + left + right

        dfs(root)
        return ans
# @lc code=end
