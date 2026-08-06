"""
Approach: Trie plus DFS for wildcard search.
Data structure: trie nodes store character edges and an end marker, allowing prefix pruning during search.
Interview logic: normal characters follow one edge. The '.' wildcard branches to every child at that position, and DFS succeeds only if some branch consumes the full pattern at a terminal word.
Complexity: addWord is O(L); search is O(L) without wildcards and O(26^d * L) worst case with d wildcards; space is O(total characters).
Tests and edge cases: searching prefixes without terminal marker returns False; '.' can match exactly one character; repeated wildcard queries traverse existing trie only.
"""
from __future__ import annotations

# @lc code=start
class WordDictionary:
    def __init__(self):
        self.root = {}

    def addWord(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.setdefault(ch, {})
        node['#'] = True

    def search(self, word: str) -> bool:
        def dfs(i: int, node: dict) -> bool:
            if i == len(word):
                return '#' in node
            ch = word[i]
            if ch == '.':
                return any(key != '#' and dfs(i + 1, child) for key, child in node.items())
            return ch in node and dfs(i + 1, node[ch])
        return dfs(0, self.root)
# @lc code=end
