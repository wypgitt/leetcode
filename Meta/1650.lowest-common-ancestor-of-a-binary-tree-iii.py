#
# @lc app=leetcode id=1650 lang=python3
#
# [1650] Lowest Common Ancestor of a Binary Tree III
#
# https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree-iii/description/
#
# algorithms
# Medium (83.02%)
# Likes:    1540
# Dislikes: 61
# Total Accepted:    409.4K
# Total Submissions: 493.2K
# Testcase Example:  "[3,5,1,6,2,0,8,null,null,7,4]\n5\n1"
#
#
# Given two nodes of a binary tree p and q, return their lowest common
# ancestor (LCA).
#
# Each node will have a reference to its parent node. The definition for
# Node is below:
#
# class Node {
#     public int val;
#     public Node left;
#     public Node right;
#     public Node parent;
# }
#
# According to the definition of LCA on Wikipedia: "The lowest common
# ancestor of two nodes p and q in a tree T is the lowest node that has
# both p and q as descendants (where we allow a node to be a descendant of
# itself)."
#
# Example 1:
#
# Input: root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 1
# Output: 3
# Explanation: The LCA of nodes 5 and 1 is 3.
#
# Example 2:
#
# Input: root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 4
# Output: 5
# Explanation: The LCA of nodes 5 and 4 is 5 since a node can be a
# descendant of itself according to the LCA definition.
#
# Example 3:
#
# Input: root = [1,2], p = 1, q = 2
# Output: 1
#
# Constraints:
#
# The number of nodes in the tree is in the range [2, 10^5].
#
# -10^9 <= Node.val <= 10^9
#
# All Node.val are unique.
#
# p != q
#
# p and q exist in the tree.
#
# @lc code=start
from typing import Optional

# Definition for a Node.
try:
    Node  # type: ignore[name-defined]
except NameError:

    class Node:  # type: ignore[no-redef]
        def __init__(self, val):
            self.val = val
            self.left = None
            self.right = None
            self.parent = None


class Solution:
    def lowestCommonAncestor(self, p: "Node", q: "Node") -> "Node":
        """
        Interview explanation:
        Premium LCA III: nodes have parent pointers (no root given). Like
        intersecting two linked lists — walk parent chains.

        Algorithm (two pointers):
        - a,b = p,q; while a!=b: a = a.parent or q; b = b.parent or p.
        - Meeting point is LCA.

        Complexity: O(h_p + h_q) time, O(1) space.
        """
        a, b = p, q
        while a is not b:
            a = a.parent if a else q
            b = b.parent if b else p
        return a

    def lowestCommonAncestor_set(self, p: "Node", q: "Node") -> "Node":
        """
        Interview explanation:
        Alternate: put all ancestors of p in a set; climb q until hit the set.

        Algorithm (ancestor set):
        - while p: add p; p=p.parent. while q not in set: q=q.parent.

        Complexity: O(h) time/space.
        """
        seen = set()
        while p:
            seen.add(p)
            p = p.parent
        while q not in seen:
            q = q.parent
        return q
# @lc code=end
