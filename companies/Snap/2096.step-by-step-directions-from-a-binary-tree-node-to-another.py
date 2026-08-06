#
# @lc app=leetcode id=2096 lang=python3
#
# [2096] Step-By-Step Directions From a Binary Tree Node to Another
#
# https://leetcode.com/problems/step-by-step-directions-from-a-binary-tree-node-to-another/description/
#
# algorithms
# Medium (56.46%)
# Likes:    3292
# Dislikes: 171
# Total Accepted:    243.7K
# Total Submissions: 431.7K
# Testcase Example:  "[5,1,2,3,null,6,4]\n3\n6"
#
# You are given the root of a binary tree with n nodes. Each node is uniquely
# assigned a value from 1 to n. You are also given an integer startValue
# representing the value of the start node s, and a different integer destValue
# representing the value of the destination node t.
#
# Find the shortest path starting from node s and ending at node t. Generate
# step-by-step directions of such path as a string consisting of only the
# uppercase letters 'L', 'R', and 'U'. Each letter indicates a specific
# direction:
#
#
# 'L' means to go from a node to its left child node.
#
#
# 'R' means to go from a node to its right child node.
#
#
# 'U' means to go from a node to its parent node.
#
# Return the step-by-step directions of the shortest path from node s to node t.
#
#
#
# Example 1:
#
# Input: root = [5,1,2,3,null,6,4], startValue = 3, destValue = 6
# Output: "UURL"
# Explanation: The shortest path is: 3 → 1 → 5 → 2 → 6.
#
# Example 2:
#
# Input: root = [2,1], startValue = 2, destValue = 1
# Output: "L"
# Explanation: The shortest path is: 2 → 1.
#
#
#
# Constraints:
#
#
# The number of nodes in the tree is n.
#
#
# 2 <= n <= 10^5
#
#
# 1 <= Node.val <= n
#
#
# All the values in the tree are unique.
#
#
# 1 <= startValue, destValue <= n
#
#
# startValue != destValue
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
    def getDirections(self, root: Optional[TreeNode], startValue: int, destValue: int) -> str:
        """
        Interview explanation:
        Shortest path directions from start to dest in a binary tree using
        L/R/U moves. Go up to LCA then down to destination.

        Algorithm:
        - DFS paths from root to start and dest as L/R strings; strip common
          prefix (LCA); answer = 'U'*len(start_suffix) + dest_suffix.

        Complexity: O(n) time, O(h) space.
        """
        def find(node: Optional[TreeNode], target: int, path: list) -> bool:
            if not node:
                return False
            if node.val == target:
                return True
            path.append('L')
            if find(node.left, target, path):
                return True
            path.pop()
            path.append('R')
            if find(node.right, target, path):
                return True
            path.pop()
            return False

        ps, pd = [], []
        find(root, startValue, ps)
        find(root, destValue, pd)
        i = 0
        while i < len(ps) and i < len(pd) and ps[i] == pd[i]:
            i += 1
        return 'U' * (len(ps) - i) + ''.join(pd[i:])

    def getDirections_lca(self, root: Optional[TreeNode], startValue: int, destValue: int) -> str:
        """
        Interview explanation:
        Alternate: explicitly find LCA, then path start→LCA (all U) and LCA→dest.

        Algorithm:
        - Standard LCA; DFS directions from LCA to each node; combine.

        Complexity: O(n) time, O(h) space.
        """
        def lca(node):
            if not node or node.val in (startValue, destValue):
                return node
            L, R = lca(node.left), lca(node.right)
            if L and R:
                return node
            return L or R

        def path_to(node, target, path):
            if not node:
                return False
            if node.val == target:
                return True
            path.append('L')
            if path_to(node.left, target, path):
                return True
            path[-1] = 'R'
            if path_to(node.right, target, path):
                return True
            path.pop()
            return False

        node = lca(root)
        ps, pd = [], []
        path_to(node, startValue, ps)
        path_to(node, destValue, pd)
        return 'U' * len(ps) + ''.join(pd)
# @lc code=end
