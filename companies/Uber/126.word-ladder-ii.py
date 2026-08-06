#
# @lc app=leetcode id=126 lang=python3
#
# [126] Word Ladder II
#
# https://leetcode.com/problems/word-ladder-ii/description/
#
# algorithms
# Hard (27.92%)
# Likes:    6662
# Dislikes: 838
# Total Accepted:    481K
# Total Submissions: 1.7M
# Testcase Example:  "\"hit\""
#
# A transformation sequence from word beginWord to word endWord using a
# dictionary wordList is a sequence of words beginWord -> s_1 -> s_2 -> ... ->
# s_k such that:
#
# Every adjacent pair of words differs by a single letter.
#
# Every s_i for 1 <= i <= k is in wordList. Note that beginWord does not need
# to be in wordList.
#
# s_k == endWord
#
# Given two words, beginWord and endWord, and a dictionary wordList, return all
# the shortest transformation sequences from beginWord to endWord, or an empty
# list if no such sequence exists. Each sequence should be returned as a list
# of the words [beginWord, s_1, s_2, ..., s_k].
#
# Example 1:
#
# Input: beginWord = "hit", endWord = "cog", wordList =
# ["hot","dot","dog","lot","log","cog"]
# Output: [["hit","hot","dot","dog","cog"],["hit","hot","lot","log","cog"]]
# Explanation: There are 2 shortest transformation sequences:
# "hit" -> "hot" -> "dot" -> "dog" -> "cog"
# "hit" -> "hot" -> "lot" -> "log" -> "cog"
#
# Example 2:
#
# Input: beginWord = "hit", endWord = "cog", wordList =
# ["hot","dot","dog","lot","log"]
# Output: []
# Explanation: The endWord "cog" is not in wordList, therefore there is no
# valid transformation sequence.
#
# Constraints:
#
# 1 <= beginWord.length <= 5
#
# endWord.length == beginWord.length
#
# 1 <= wordList.length <= 500
#
# wordList[i].length == beginWord.length
#
# beginWord, endWord, and wordList[i] consist of lowercase English letters.
#
# beginWord != endWord
#
# All the words in wordList are unique.
#
# The sum of all shortest transformation sequences does not exceed 10^5.
#

# @lc code=start
from collections import defaultdict, deque
from typing import Dict, List, Set


class Solution:
    def findLadders(
        self, beginWord: str, endWord: str, wordList: List[str]
    ) -> List[List[str]]:
        """
        Interview explanation:
        Classic shortest-path enumeration: BFS from beginWord builds a DAG of
        parents only along shortest edges, then DFS/backtracking reconstructs
        every shortest path from endWord back to beginWord.

        Algorithm:
        - Put wordList in a set; BFS level by level.
        - For each word, try all one-letter neighbors still in the unused set.
        - Record parents[neighbor].append(word) for edges discovered at the
          first (shortest) distance; do not reuse a word in later levels.
        - From endWord, DFS parents to emit reversed paths.

        Complexity: O(N * L^2 + P * L) time where N is dictionary size, L word
        length, P number of shortest paths; O(N * L + P * L) space.
        """
        word_set: Set[str] = set(wordList)
        if endWord not in word_set:
            return []

        parents: Dict[str, List[str]] = defaultdict(list)
        queue = deque([beginWord])
        found = False
        word_set.discard(beginWord)

        while queue and not found:
            level_visited: Set[str] = set()
            for _ in range(len(queue)):
                word = queue.popleft()
                chars = list(word)
                for i in range(len(chars)):
                    original = chars[i]
                    for c in "abcdefghijklmnopqrstuvwxyz":
                        if c == original:
                            continue
                        chars[i] = c
                        nxt = "".join(chars)
                        if nxt in word_set:
                            if nxt not in level_visited:
                                level_visited.add(nxt)
                                queue.append(nxt)
                            parents[nxt].append(word)
                            if nxt == endWord:
                                found = True
                    chars[i] = original
            word_set -= level_visited

        if not found:
            return []

        paths: List[List[str]] = []
        path = [endWord]

        def dfs(word: str) -> None:
            if word == beginWord:
                paths.append(path[::-1])
                return
            for prev in parents[word]:
                path.append(prev)
                dfs(prev)
                path.pop()

        dfs(endWord)
        return paths
# @lc code=end
