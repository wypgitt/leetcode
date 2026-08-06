"""
Approach: Build a sorted list by inserting each original node into its correct place.
Data structure: a dummy head simplifies insertion at the front of the sorted prefix.
Interview logic: before processing each node, dummy.next is sorted. Splicing the next node after the last smaller sorted node preserves that invariant.
Complexity: O(n^2) time, O(1) extra space.
Tests and edge cases: empty list; already sorted list; reverse-sorted list; duplicates stay valid.
"""
from __future__ import annotations
from typing import Optional

# @lc code=start
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def insertionSortList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode(0)
        cur = head
        while cur:
            nxt = cur.next
            prev = dummy
            while prev.next and prev.next.val < cur.val:
                prev = prev.next
            cur.next = prev.next
            prev.next = cur
            cur = nxt
        return dummy.next
# @lc code=end
