#
# @lc app=leetcode id=100 lang=python3
#
# [100] Same Tree
#
# https://leetcode.com/problems/same-tree/description/
#
# algorithms
# Easy (67.71%)
# Likes:    13056
# Dislikes: 306
# Total Accepted:    3.6M
# Total Submissions: 5.3M
# Testcase Example:  "[1,2,3]"
#
# Given the roots of two binary trees p and q, write a function to check if
# they are the same or not.
#
# Two binary trees are considered the same if they are structurally identical,
# and the nodes have the same value.
#
# Example 1:
#
# Input: p = [1,2,3], q = [1,2,3]
# Output: true
#
# Example 2:
#
# Input: p = [1,2], q = [1,null,2]
# Output: false
#
# Example 3:
#
# Input: p = [1,2,1], q = [1,1,2]
# Output: false
#
# Constraints:
#
# The number of nodes in both trees is in the range [0, 100].
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
    def isSameTree(self, p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
        """
        Interview explanation:
        Two trees are the same only when every corresponding pair of nodes
        matches in both structure and value. DFS compares one pair at a time.

        Algorithm:
        - Both None -> True.
        - One None or values differ -> False.
        - Otherwise recurse on left children and right children.

        Complexity: O(n) time, O(h) recursion space.
        """
        if not p and not q:
            return True
        if not p or not q or p.val != q.val:
            return False
        return self.isSameTree(p.left, q.left) and self.isSameTree(p.right, q.right)

    def isSameTreeBFS(self, p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
        """
        Interview explanation:
        BFS compares trees level-by-level with a queue of node pairs, which is
        useful when you want an iterative solution or early exit on mismatch.

        Algorithm:
        - Queue stores (node from p, node from q).
        - For each pair, check nullity and values, then enqueue children pairs.

        Complexity: O(n) time, O(w) queue space for maximum width w.
        """
        queue = deque([(p, q)])
        while queue:
            a, b = queue.popleft()
            if not a and not b:
                continue
            if not a or not b or a.val != b.val:
                return False
            queue.append((a.left, b.left))
            queue.append((a.right, b.right))
        return True
# @lc code=end
