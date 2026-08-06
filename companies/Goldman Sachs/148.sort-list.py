"""
Approach: Merge sort on the linked list.
Data structure: slow/fast pointers split the list, and pointer-based merge avoids arrays.
Interview logic: recursively sort two halves, then merge by repeatedly taking the smaller front node. Merge sort is preferred for linked lists because merging is O(1) per node without random access.
Complexity: O(n log n) time, O(log n) recursion stack; bottom-up merge sort can improve space to O(1).
Tests and edge cases: empty and single-node lists are base cases; duplicates and negative values compare normally.
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
    def sortList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        if not head or not head.next:
            return head
        slow, fast = head, head.next
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
        second = slow.next
        slow.next = None
        return self._merge(self.sortList(head), self.sortList(second))

    def _merge(self, a: Optional[ListNode], b: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode(0)
        tail = dummy
        while a and b:
            if a.val <= b.val:
                tail.next, a = a, a.next
            else:
                tail.next, b = b, b.next
            tail = tail.next
        tail.next = a or b
        return dummy.next
# @lc code=end
