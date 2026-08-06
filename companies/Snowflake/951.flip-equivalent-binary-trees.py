#
# @lc app=leetcode id=951 lang=python3
#
# [951] Flip Equivalent Binary Trees
#
# https://leetcode.com/problems/flip-equivalent-binary-trees/description/
#
# algorithms
# Medium (69.49%)
# Likes:    2904
# Dislikes: 125
# Total Accepted:    274K
# Total Submissions: 394K
# Testcase Example:  "[1,2,3,4,5,6,null,null,null,7,8]"
#
# For a binary tree T, we can define a flip operation as follows: choose any
# node, and swap the left and right child subtrees.
#
# A binary tree X is flip equivalent to a binary tree Y if and only if we can
# make X equal to Y after some number of flip operations.
#
# Given the roots of two binary trees root1 and root2, return true if the two
# trees are flip equivalent or false otherwise.
#
# Example 1:
#
# Input: root1 = [1,2,3,4,5,6,null,null,null,7,8], root2 =
# [1,3,2,null,6,4,5,null,null,null,null,8,7]
# Output: true
# Explanation: We flipped at nodes with values 1, 3, and 5.
#
# Example 2:
#
# Input: root1 = [], root2 = []
# Output: true
#
# Example 3:
#
# Input: root1 = [], root2 = [1]
# Output: false
#
# Constraints:
#
# The number of nodes in each tree is in the range [0, 100].
#
# Each tree will have unique node values in the range [0, 99].
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
    def flipEquiv(self, root1: Optional[TreeNode], root2: Optional[TreeNode]) -> bool:
        """
        Interview explanation:
        Flip-equivalent if equal after any number of child swaps. Recursively:
        same value, and children match either unflipped or flipped pairing.

        Algorithm (recursive):
        - If both None: True; one None or vals differ: False
        - Return (flipEquiv(L1,L2) and flipEquiv(R1,R2)) or
                 (flipEquiv(L1,R2) and flipEquiv(R1,L2))

        Complexity: O(min(n1,n2)) time, O(h) space.
        """
        if root1 is root2:
            return True
        if not root1 or not root2 or root1.val != root2.val:
            return False
        return (
            self.flipEquiv(root1.left, root2.left)
            and self.flipEquiv(root1.right, root2.right)
        ) or (
            self.flipEquiv(root1.left, root2.right)
            and self.flipEquiv(root1.right, root2.left)
        )

    def flipEquiv_bfs(self, root1: Optional[TreeNode], root2: Optional[TreeNode]) -> bool:
        """
        Interview explanation:
        Alternate: BFS/queue pairs of nodes; at each pair, children may be
        matched straight or crossed after sorting by value presence.

        Algorithm (BFS):
        - Queue of (n1,n2); while: check vals; gather children lists; try match
          by sorting children by val (None as sentinel) — if multisets of child
          vals differ fail; enqueue matched pairs by value

        Complexity: O(n) time, O(n) space.
        """
        q = deque([(root1, root2)])
        while q:
            a, b = q.popleft()
            if not a and not b:
                continue
            if not a or not b or a.val != b.val:
                return False
            a_children = [c for c in (a.left, a.right) if c]
            b_children = [c for c in (b.left, b.right) if c]
            if len(a_children) != len(b_children):
                return False
            a_children.sort(key=lambda x: x.val)
            b_children.sort(key=lambda x: x.val)
            if [c.val for c in a_children] != [c.val for c in b_children]:
                return False
            for ca, cb in zip(a_children, b_children):
                q.append((ca, cb))
        return True
# @lc code=end

