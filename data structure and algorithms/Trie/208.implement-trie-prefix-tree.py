"""
Approach: Trie with nested dictionaries and an end-of-word marker.
Data structure: each node maps characters to child nodes; a boolean marker distinguishes full words from prefixes.
Interview logic: insert creates missing child edges, search requires consuming every character and seeing the terminal marker, and startsWith only requires consuming the prefix.
Complexity: O(L) time per operation, O(total inserted characters) space.
Tests and edge cases: searching a prefix before it is inserted as a word returns False; empty prefix is supported; shared prefixes reuse nodes.
"""
from __future__ import annotations

# @lc code=start
class Trie:
    def __init__(self):
        self.root = {}

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.setdefault(ch, {})
        node['#'] = True

    def search(self, word: str) -> bool:
        node = self.root
        for ch in word:
            if ch not in node:
                return False
            node = node[ch]
        return '#' in node

    def startsWith(self, prefix: str) -> bool:
        node = self.root
        for ch in prefix:
            if ch not in node:
                return False
            node = node[ch]
        return True
# @lc code=end
