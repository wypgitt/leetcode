"""
Approach: DFS clone with a dictionary from original node objects to cloned node objects.
Data structure: the dictionary preserves graph identity and prevents infinite recursion on cycles.
Interview logic: create each clone once, memoize it immediately, then fill its neighbor list by recursively cloning neighbors. Shared neighbors and self-loops then point to the correct shared clone.
Complexity: O(V + E) time, O(V) space.
Tests and edge cases: None returns None; cycles terminate through the memo map; disconnected nodes outside the input component are irrelevant.
"""
from __future__ import annotations
from typing import Optional

# @lc code=start
"""
# Definition for a Node.
class Node:
    def __init__(self, val = 0, neighbors = None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []
"""
class Solution:
    def cloneGraph(self, node: Optional['Node']) -> Optional['Node']:
        clones = {}
        def clone(cur: Optional['Node']) -> Optional['Node']:
            if cur is None:
                return None
            if cur in clones:
                return clones[cur]
            copied = Node(cur.val)
            clones[cur] = copied
            copied.neighbors = [clone(nei) for nei in cur.neighbors]
            return copied
        return clone(node)
# @lc code=end
