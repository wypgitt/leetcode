"""
Approach: Floyd slow/fast pointers, followed by entry-location walk.
Data structure: two pointers replace a visited set, keeping constant space.
Interview logic: after slow and fast meet inside the cycle, resetting one pointer to head and moving both one step makes them meet at the cycle entry by the cycle-distance equation.
Complexity: O(n) time, O(1) space.
Tests and edge cases: no cycle returns None; one-node self-cycle returns that node; cycle at head works.
"""
from __future__ import annotations
from typing import Optional

# @lc code=start
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None
class Solution:
    def detectCycle(self, head: Optional[ListNode]) -> Optional[ListNode]:
        slow = fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
            if slow is fast:
                finder = head
                while finder is not slow:
                    finder = finder.next
                    slow = slow.next
                return finder
        return None
# @lc code=end
