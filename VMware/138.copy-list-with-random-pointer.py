"""
Approach: Interleave copied nodes with originals, assign random pointers, then detach.
Data structure: the list itself temporarily acts as the original-to-copy map because each copy is original.next.
Interview logic: after weaving A -> A' -> B -> B', the clone of cur.random is cur.random.next. Once random pointers are assigned, restore original next links and extract the copied list.
Complexity: O(n) time, O(1) extra space excluding output nodes.
Tests and edge cases: empty list returns None; random may be None; self-random and random cycles copy correctly.
"""
from __future__ import annotations
from typing import Optional

# @lc code=start
"""
# Definition for a Node.
class Node:
    def __init__(self, x: int, next: 'Node' = None, random: 'Node' = None):
        self.val = int(x)
        self.next = next
        self.random = random
"""
class Solution:
    def copyRandomList(self, head: 'Optional[Node]') -> 'Optional[Node]':
        if not head:
            return None
        cur = head
        while cur:
            cur.next = Node(cur.val, cur.next)
            cur = cur.next.next
        cur = head
        while cur:
            if cur.random:
                cur.next.random = cur.random.next
            cur = cur.next.next
        cur = head
        copied_head = head.next
        while cur:
            copied = cur.next
            cur.next = copied.next
            cur = cur.next
            copied.next = cur.next if cur else None
        return copied_head
# @lc code=end
