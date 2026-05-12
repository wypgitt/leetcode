from __future__ import annotations

from typing import Optional


# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def removeZeroSumSublists(self, head: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode(0, head)
        prefix_to_node = {}
        prefix = 0
        node = dummy

        while node:
            prefix += node.val
            prefix_to_node[prefix] = node
            node = node.next

        prefix = 0
        node = dummy
        while node:
            prefix += node.val
            node.next = prefix_to_node[prefix].next
            node = node.next

        return dummy.next

