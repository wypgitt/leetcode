"""
Approach: Copy the next node's value into the current node, then bypass the next node.
Data structure: direct linked-list pointer mutation; no head pointer is available or needed.
Interview logic: since the node to delete is guaranteed not to be the tail, we can make it look like its successor and remove the successor instead.
Complexity: O(1) time, O(1) space.
Tests and edge cases: deleting middle nodes; deleting the node before tail; tail deletion is intentionally outside the problem constraints.
"""
from __future__ import annotations

# @lc code=start
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None
class Solution:
    def deleteNode(self, node):
        node.val = node.next.val
        node.next = node.next.next
# @lc code=end
