#
# @lc app=leetcode id=109 lang=python3
#
# [109] Convert Sorted List to Binary Search Tree
#
# https://leetcode.com/problems/convert-sorted-list-to-binary-search-tree/description/
#
# algorithms
# Medium (66.57%)
# Likes:    7896
# Dislikes: 175
# Total Accepted:    692.6K
# Total Submissions: 1M
# Testcase Example:  '[-10,-3,0,5,9]'
#
# Given the head of a singly linked list where elements are sorted in ascending
# order, convert it to a height-balanced binary search tree.
# 
# 
# Example 1:
# 
# 
# Input: head = [-10,-3,0,5,9]
# Output: [0,-3,9,-10,null,5]
# Explanation: One possible answer is [0,-3,9,-10,null,5], which represents the
# shown height balanced BST.
# 
# 
# Example 2:
# 
# 
# Input: head = []
# Output: []
# 
# 
# 
# Constraints:
# 
# 
# The number of nodes in head is in the range [0, 2 * 10^4].
# -10^5 <= Node.val <= 10^5
# 
# 
#

# @lc code=start
from typing import List, Optional
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def sortedListToBST(self, head: Optional[ListNode]) -> Optional[TreeNode]:
        """
        Interview explanation:
        A height-balanced BST should use the middle list value as root. The most
        efficient linked-list approach counts nodes, then simulates inorder tree
        construction. Build the left subtree for the first half, consume the
        current list node as root, then build the right subtree. This uses the
        sorted order exactly once.

        Edge cases and tests:
        - Empty list returns None.
        - One node becomes a leaf.
        - Even length can choose either middle; this implementation chooses the
          upper middle through inorder sizing.

        Complexity: O(n) time, O(log n) recursion space for a balanced tree.
        """
        length = 0
        cur = head
        while cur:
            length += 1
            cur = cur.next

        current = head

        def build(size: int) -> Optional[TreeNode]:
            nonlocal current
            if size <= 0:
                return None
            left = build(size // 2)
            root = TreeNode(current.val)
            current = current.next
            root.left = left
            root.right = build(size - size // 2 - 1)
            return root

        return build(length)
# @lc code=end


