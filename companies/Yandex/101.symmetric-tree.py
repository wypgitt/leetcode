#
# @lc app=leetcode id=101 lang=python3
#
# [101] Symmetric Tree
#
# https://leetcode.com/problems/symmetric-tree/description/
#
# algorithms
# Easy (61.75%)
# Likes:    17013
# Dislikes: 465
# Total Accepted:    3.0M
# Total Submissions: 4.9M
# Testcase Example:  "[1,2,2,3,4,4,3]"
#
# Given the root of a binary tree, check whether it is a mirror of itself
# (i.e., symmetric around its center).
#
# Example 1:
#
# Input: root = [1,2,2,3,4,4,3]
# Output: true
#
# Example 2:
#
# Input: root = [1,2,2,null,3,null,3]
# Output: false
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 1000].
#
# -100 <= Node.val <= 100
#
# Follow up: Could you solve it both recursively and iteratively?
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
    def isSymmetric(self, root: Optional[TreeNode]) -> bool:
        """
        Interview explanation:
        A tree is symmetric if its left and right subtrees are mirrors of each
        other. Recursively compare outer children with outer children and inner
        with inner.

        Algorithm:
        - Define mirror(a, b): both None ok; one None fail; values equal and
          mirror(a.left, b.right) and mirror(a.right, b.left).
        - Start with mirror(root.left, root.right).

        Complexity: O(n) time, O(h) recursion space.
        """
        def mirror(a: Optional[TreeNode], b: Optional[TreeNode]) -> bool:
            if not a and not b:
                return True
            if not a or not b or a.val != b.val:
                return False
            return mirror(a.left, b.right) and mirror(a.right, b.left)

        return mirror(root.left, root.right) if root else True

    def isSymmetricBFS(self, root: Optional[TreeNode]) -> bool:
        """
        Interview explanation:
        Iterative BFS/queue checks mirrored positions side by side without
        recursion, which interviewers often ask as a follow-up.

        Algorithm:
        - Seed the queue with (left, right).
        - For each pair, validate nullity/values, then enqueue
          (a.left, b.right) and (a.right, b.left).

        Complexity: O(n) time, O(w) queue space.
        """
        if not root:
            return True
        queue = deque([(root.left, root.right)])
        while queue:
            a, b = queue.popleft()
            if not a and not b:
                continue
            if not a or not b or a.val != b.val:
                return False
            queue.append((a.left, b.right))
            queue.append((a.right, b.left))
        return True
# @lc code=end
