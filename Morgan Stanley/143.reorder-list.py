"""
Approach: Find the middle, reverse the second half, and merge alternating nodes.
Data structure: in-place linked-list pointer rewiring gives O(1) extra space.
Interview logic: the target order L0,Ln,L1,Ln-1,... is the first half interleaved with the reversed second half.
Complexity: O(n) time, O(1) space.
Tests and edge cases: empty or one node is unchanged; odd length leaves the middle last; even length alternates cleanly.
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
    def reorderList(self, head: Optional[ListNode]) -> None:
        if not head or not head.next:
            return
        slow, fast = head, head.next
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
        second = slow.next
        slow.next = None
        prev = None
        while second:
            nxt = second.next
            second.next = prev
            prev = second
            second = nxt
        first, second = head, prev
        while second:
            fnext, snext = first.next, second.next
            first.next = second
            second.next = fnext
            first, second = fnext, snext
# @lc code=end
