"""
Approach: Hash map plus doubly linked list.
Data structure: the map gives O(1) key lookup; the linked list gives O(1) removal and insertion for recency updates.
Interview logic: keep least recently used near the dummy head and most recently used near the dummy tail. get and existing-key put move a node to the tail; over-capacity put evicts head.next.
Complexity: O(1) average time per operation, O(capacity) space.
Tests and edge cases: capacity 1; updating an existing key must not evict; missing get returns -1.
"""
from __future__ import annotations

# @lc code=start
class _Node:
    def __init__(self, key: int = 0, value: int = 0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.nodes = {}
        self.head = _Node()
        self.tail = _Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: _Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_back(self, node: _Node) -> None:
        last = self.tail.prev
        last.next = node
        node.prev = last
        node.next = self.tail
        self.tail.prev = node

    def _mark_used(self, node: _Node) -> None:
        self._remove(node)
        self._add_to_back(node)

    def get(self, key: int) -> int:
        if key not in self.nodes:
            return -1
        node = self.nodes[key]
        self._mark_used(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        if key in self.nodes:
            node = self.nodes[key]
            node.value = value
            self._mark_used(node)
            return
        node = _Node(key, value)
        self.nodes[key] = node
        self._add_to_back(node)
        if len(self.nodes) > self.capacity:
            lru = self.head.next
            self._remove(lru)
            del self.nodes[lru.key]
# @lc code=end
