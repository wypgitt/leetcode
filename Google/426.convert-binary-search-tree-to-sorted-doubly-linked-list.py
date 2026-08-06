#
# @lc app=leetcode id=426 lang=python3
#
# [426] Convert Binary Search Tree to Sorted Doubly Linked List
#
# https://leetcode.com/problems/convert-binary-search-tree-to-sorted-doubly-linked-list/description/
#
# algorithms
# Medium (65.63%)
# Likes:    2732
# Dislikes: 245
# Total Accepted:    373.6K
# Total Submissions: 569.3K
# Testcase Example:  "[4,2,5,1,3]"
#
#
# Convert a Binary Search Tree to a sorted Circular Doubly-Linked List in
# place.
#
# You can think of the left and right pointers as synonymous to the
# predecessor and successor pointers in a doubly-linked list. For a
# circular doubly linked list, the predecessor of the first element is the
# last element, and the successor of the last element is the first
# element.
#
# We want to do the transformation in place. After the transformation, the
# left pointer of the tree node should point to its predecessor, and the
# right pointer should point to its successor. You should return the
# pointer to the smallest element of the linked list.
#
# Example 1:
#
# Input: root = [4,2,5,1,3]
#
# Output: [1,2,3,4,5]
#
# Explanation: The figure below shows the transformed BST. The solid line
# indicates the successor relationship, while the dashed line means the
# predecessor relationship.
#
# Example 2:
#
# Input: root = [2,1,3]
# Output: [1,2,3]
#
# Constraints:
#
# The number of nodes in the tree is in the range [0, 2000].
#
# -1000 <= Node.val <= 1000
#
# All the values of the tree are unique.
#
# @lc code=start

from typing import Optional


# Definition for a Node.
class Node:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def treeToDoublyList(self, root: "Optional[Node]") -> "Optional[Node]":
        """
        Interview explanation:
        Inorder traversal of a BST yields sorted order. Link each visited node
        to the previous one (prev.right = cur, cur.left = prev), then connect
        head and tail into a circular DLL.

        Algorithm:
        - Inorder DFS; maintain prev and first.
        - After traversal, first.left = last, last.right = first.

        Complexity: O(n) time, O(h) recursion space.
        """
        if not root:
            return None
        first = prev = None

        def inorder(node: Node) -> None:
            nonlocal first, prev
            if not node:
                return
            inorder(node.left)
            if prev:
                prev.right = node
                node.left = prev
            else:
                first = node
            prev = node
            inorder(node.right)

        inorder(root)
        first.left = prev
        prev.right = first
        return first
# @lc code=end
