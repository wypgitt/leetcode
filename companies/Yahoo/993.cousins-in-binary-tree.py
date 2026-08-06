#
# @lc app=leetcode id=993 lang=python3
#
# [993] Cousins in Binary Tree
#
# https://leetcode.com/problems/cousins-in-binary-tree/description/
#
# algorithms
# Easy (59.63%)
# Likes:    4355
# Dislikes: 237
# Total Accepted:    360K
# Total Submissions: 604K
# Testcase Example:  "[1,2,3,4]"
#
# Given the root of a binary tree with unique values and the values of two
# different nodes of the tree x and y, return true if the nodes corresponding
# to the values x and y in the tree are cousins, or false otherwise.
#
# Two nodes of a binary tree are cousins if they have the same depth with
# different parents.
#
# Note that in a binary tree, the root node is at the depth 0, and children of
# each depth k node are at the depth k + 1.
#
# Example 1:
#
# Input: root = [1,2,3,4], x = 4, y = 3
# Output: false
#
# Example 2:
#
# Input: root = [1,2,3,null,4,null,5], x = 5, y = 4
# Output: true
#
# Example 3:
#
# Input: root = [1,2,3,null,4], x = 2, y = 3
# Output: false
#
# Constraints:
#
# The number of nodes in the tree is in the range [2, 100].
#
# 1 <= Node.val <= 100
#
# Each node has a unique value.
#
# x != y
#
# x and y are exist in the tree.
#

# @lc code=start
from collections import deque
from typing import Optional
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right


class Solution:
    def isCousins(self, root: Optional[TreeNode], x: int, y: int) -> bool:
        """
        Interview explanation:
        Cousins share depth but not parent. BFS level-order tracking parent of
        each child; when both x and y appear in the same level with different
        parents, return True.

        Algorithm (BFS):
        - Queue of (node, parent). Per level, record parent of x and of y if seen.
        - After a level: if both found return parents differ; if one found False.

        Complexity: O(n) time, O(n) space.
        """
        if not root:
            return False
        q = deque([(root, None)])
        while q:
            px = py = None
            found_x = found_y = False
            for _ in range(len(q)):
                node, parent = q.popleft()
                if node.val == x:
                    found_x, px = True, parent
                if node.val == y:
                    found_y, py = True, parent
                if node.left:
                    q.append((node.left, node))
                if node.right:
                    q.append((node.right, node))
            if found_x and found_y:
                return px is not py
            if found_x or found_y:
                return False
        return False

    def isCousins_dfs(self, root: Optional[TreeNode], x: int, y: int) -> bool:
        """
        Interview explanation:
        Alternate DFS: record (depth, parent) for x and y; cousins iff same
        depth and different parents.

        Algorithm:
        - dfs(node, parent, depth): when val is x or y, store info.
        - Compare recorded depths and parents.

        Complexity: O(n) time, O(h) space.
        """
        info = {}

        def dfs(node: Optional[TreeNode], parent: Optional[TreeNode], depth: int) -> None:
            if not node or len(info) == 2:
                return
            if node.val in (x, y):
                info[node.val] = (depth, parent)
            dfs(node.left, node, depth + 1)
            dfs(node.right, node, depth + 1)

        dfs(root, None, 0)
        dx, px = info[x]
        dy, py = info[y]
        return dx == dy and px is not py
# @lc code=end
