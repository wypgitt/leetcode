#
# @lc app=leetcode id=1367 lang=python3
#
# [1367] Linked List in Binary Tree
#
# https://leetcode.com/problems/linked-list-in-binary-tree/description/
#
# algorithms
# Medium (51.96%)
# Likes:    3029
# Dislikes: 90
# Total Accepted:    210K
# Total Submissions: 404.2K
# Testcase Example:  '[4,2,8]\n[1,4,4,null,2,2,null,1,null,6,8,null,null,null,null,1,3]'
#
# Given a binary tree root and a linked list with head as the first node. 
# 
# Return True if all the elements in the linked list starting from the head
# correspond to some downward path connected in the binary tree otherwise
# return False.
# 
# In this context downward path means a path that starts at some node and goes
# downwards.
# 
# 
# Example 1:
# 
# 
# 
# 
# Input: head = [4,2,8], root =
# [1,4,4,null,2,2,null,1,null,6,8,null,null,null,null,1,3]
# Output: true
# Explanation: Nodes in blue form a subpath in the binary Tree.  
# 
# 
# Example 2:
# 
# 
# 
# 
# Input: head = [1,4,2,6], root =
# [1,4,4,null,2,2,null,1,null,6,8,null,null,null,null,1,3]
# Output: true
# 
# 
# Example 3:
# 
# 
# Input: head = [1,4,2,6,8], root =
# [1,4,4,null,2,2,null,1,null,6,8,null,null,null,null,1,3]
# Output: false
# Explanation: There is no path in the binary tree that contains all the
# elements of the linked list from head.
# 
# 
# 
# Constraints:
# 
# 
# The number of nodes in the tree will be in the range [1, 2500].
# The number of nodes in the list will be in the range [1, 100].
# 1 <= Node.val <= 100 for each node in the linked list and binary tree.
# 
# 
#

# @lc code=start
from __future__ import annotations

from typing import Optional


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
    def isSubPath(self, head: Optional[ListNode], root: Optional[TreeNode]) -> bool:
        def matches(list_node: Optional[ListNode], tree_node: Optional[TreeNode]) -> bool:
            if list_node is None:
                return True
            if tree_node is None or tree_node.val != list_node.val:
                return False
            return (
                matches(list_node.next, tree_node.left)
                or matches(list_node.next, tree_node.right)
            )

        if root is None:
            return False

        return (
            matches(head, root)
            or self.isSubPath(head, root.left)
            or self.isSubPath(head, root.right)
        )
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# A linked list can start at any tree node, but once it starts, it must follow a
# downward path. So for each tree node, try to match the list from there.
#
# Data structure:
# Recursion handles both searches:
# - `isSubPath` scans for possible starting tree nodes.
# - `matches` checks whether the linked list continues down from one start.
#
# Walkthrough:
# 1. `matches` succeeds if the whole list has been consumed.
# 2. It fails if the tree path ends or values differ.
# 3. Otherwise, it tries matching the next list node with either child.
# 4. `isSubPath` runs this check at the current node, then recursively tries
#    the left and right subtrees as alternative starts.
#
# Edge cases:
# - Empty tree: no non-empty list path exists.
# - List longer than a path: `tree_node is None` stops that attempt.
# - Duplicate values: every possible start is checked.
#
# Complexity:
# - Time: O(n * m) in the worst case, where n is tree nodes and m is list
#   length.
# - Space: O(h + m) recursion depth in the nested calls.
#
# Improvement:
# For much larger constraints, we could use KMP over root-to-node paths to
# reduce repeated matching, but the direct recursion is clear and accepted here.
