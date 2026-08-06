#
# @lc app=leetcode id=617 lang=python3
#
# [617] Merge Two Binary Trees
#
# https://leetcode.com/problems/merge-two-binary-trees/description/
#
# algorithms
# Easy (79.13%)
# Likes:    9095
# Dislikes: 326
# Total Accepted:    913K
# Total Submissions: 1.2M
# Testcase Example:  "[1,3,2,5]"
#
# You are given two binary trees root1 and root2.
#
# Imagine that when you put one of them to cover the other, some nodes of the
# two trees are overlapped while the others are not. You need to merge the two
# trees into a new binary tree. The merge rule is that if two nodes overlap,
# then sum node values up as the new value of the merged node. Otherwise, the
# NOT null node will be used as the node of the new tree.
#
# Return the merged tree.
#
# Note: The merging process must start from the root nodes of both trees.
#
# Example 1:
#
# Input: root1 = [1,3,2,5], root2 = [2,1,3,null,4,null,7]
# Output: [3,4,5,5,4,null,7]
#
# Example 2:
#
# Input: root1 = [1], root2 = [1,2]
# Output: [2,2]
#
# Constraints:
#
# The number of nodes in both trees is in the range [0, 2000].
#
# -10^4 <= Node.val <= 10^4
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
    def mergeTrees(
        self, root1: Optional[TreeNode], root2: Optional[TreeNode]
    ) -> Optional[TreeNode]:
        """
        Interview explanation:
        Merge overlapping nodes by summing values; take the non-null child when
        only one side exists. Classic recursive DFS.

        Algorithm:
        - If either null, return the other.
        - Create node with val = root1.val + root2.val; recurse on left/right.

        Complexity: O(min(N, M)) time, O(H) recursion space.
        """
        if not root1:
            return root2
        if not root2:
            return root1
        node = TreeNode(root1.val + root2.val)
        node.left = self.mergeTrees(root1.left, root2.left)
        node.right = self.mergeTrees(root1.right, root2.right)
        return node

    def mergeTrees_bfs(
        self, root1: Optional[TreeNode], root2: Optional[TreeNode]
    ) -> Optional[TreeNode]:
        """
        Interview explanation:
        Alternate classic: iterative BFS pairing corresponding nodes, summing
        values and linking missing children.

        Algorithm:
        - If either null return other. Queue pairs (n1, n2) mutating n1 as result.
        - For each child slot: if both exist sum/enqueue; elif only n2, attach.

        Complexity: O(min(N, M)) time, O(W) queue space.
        """
        if not root1:
            return root2
        if not root2:
            return root1
        root1.val += root2.val
        q = deque([(root1, root2)])
        while q:
            n1, n2 = q.popleft()
            if n2.left:
                if n1.left:
                    n1.left.val += n2.left.val
                    q.append((n1.left, n2.left))
                else:
                    n1.left = n2.left
            if n2.right:
                if n1.right:
                    n1.right.val += n2.right.val
                    q.append((n1.right, n2.right))
                else:
                    n1.right = n2.right
        return root1
# @lc code=end
