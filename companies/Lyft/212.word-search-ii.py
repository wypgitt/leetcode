#
# @lc app=leetcode id=212 lang=python3
#
# [212] Word Search II
#
# https://leetcode.com/problems/word-search-ii/description/
#
# algorithms
# Hard (38.75%)
# Likes:    10282
# Dislikes: 510
# Total Accepted:    938K
# Total Submissions: 2.4M
# Testcase Example:  "[[\"o\",\"a\",\"a\",\"n\"],[\"e\",\"t\",\"a\",\"e\"],[\"i\",\"h\",\"k\",\"r\"],[\"i\",\"f\",\"l\",\"v\"]]"
#
# Given an m x n board of characters and a list of strings words, return all
# words on the board.
#
# Each word must be constructed from letters of sequentially adjacent cells,
# where adjacent cells are horizontally or vertically neighboring. The same
# letter cell may not be used more than once in a word.
#
# Example 1:
#
# Input: board =
# [["o","a","a","n"],["e","t","a","e"],["i","h","k","r"],["i","f","l","v"]],
# words = ["oath","pea","eat","rain"]
# Output: ["eat","oath"]
#
# Example 2:
#
# Input: board = [["a","b"],["c","d"]], words = ["abcb"]
# Output: []
#
# Constraints:
#
# m == board.length
#
# n == board[i].length
#
# 1 <= m, n <= 12
#
# board[i][j] is a lowercase English letter.
#
# 1 <= words.length <= 3 * 10^4
#
# 1 <= words[i].length <= 10
#
# words[i] consists of lowercase English letters.
#
# All the strings of words are unique.
#

# @lc code=start
from typing import Dict, List, Optional


class TrieNode:
    def __init__(self) -> None:
        self.children: Dict[str, "TrieNode"] = {}
        self.word: Optional[str] = None


class Solution:
    def findWords(self, board: List[List[str]], words: List[str]) -> List[str]:
        """
        Interview explanation:
        Build a Trie of all words, then DFS/backtrack from every board cell.
        Matching on the Trie prunes dead branches; mark found words and prune
        empty Trie nodes to avoid re-search.

        Algorithm:
        - Insert all words into a Trie.
        - From each cell, DFS into neighbors if the letter continues a Trie path.
        - When a Trie node stores a word, record it and clear the word (dedupe).
        - Backtrack board visits; remove leaf children from parents when empty.

        Complexity: O(M * 4 * 3^{L-1}) search (M cells, L max word len) plus Trie build O(total chars); O(total chars) space.
        """
        root = TrieNode()
        for w in words:
            node = root
            for ch in w:
                if ch not in node.children:
                    node.children[ch] = TrieNode()
                node = node.children[ch]
            node.word = w

        rows, cols = len(board), len(board[0])
        ans: List[str] = []

        def dfs(r: int, c: int, parent: TrieNode) -> None:
            ch = board[r][c]
            node = parent.children.get(ch)
            if not node:
                return

            if node.word is not None:
                ans.append(node.word)
                node.word = None

            board[r][c] = "#"
            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != "#":
                    dfs(nr, nc, node)
            board[r][c] = ch

            if not node.children:
                parent.children.pop(ch, None)

        for i in range(rows):
            for j in range(cols):
                dfs(i, j, root)
        return ans
# @lc code=end
