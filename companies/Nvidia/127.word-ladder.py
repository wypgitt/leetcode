#
# @lc app=leetcode id=127 lang=python3
#
# [127] Word Ladder
#
# https://leetcode.com/problems/word-ladder/description/
#
# algorithms
# Hard (46.23%)
# Likes:    13679
# Dislikes: 1972
# Total Accepted:    1.7M
# Total Submissions: 3.7M
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
# Given two words, beginWord and endWord, and a dictionary wordList, return the
# number of words in the shortest transformation sequence from beginWord to
# endWord, or 0 if no such sequence exists.
#
# Example 1:
#
# Input: beginWord = "hit", endWord = "cog", wordList =
# ["hot","dot","dog","lot","log","cog"]
# Output: 5
# Explanation: One shortest transformation sequence is "hit" -> "hot" -> "dot"
# -> "dog" -> cog", which is 5 words long.
#
# Example 2:
#
# Input: beginWord = "hit", endWord = "cog", wordList =
# ["hot","dot","dog","lot","log"]
# Output: 0
# Explanation: The endWord "cog" is not in wordList, therefore there is no
# valid transformation sequence.
#
# Constraints:
#
# 1 <= beginWord.length <= 10
#
# endWord.length == beginWord.length
#
# 1 <= wordList.length <= 5000
#
# wordList[i].length == beginWord.length
#
# beginWord, endWord, and wordList[i] consist of lowercase English letters.
#
# beginWord != endWord
#
# All the words in wordList are unique.
#

# @lc code=start
from collections import deque
from typing import List, Set


class Solution:
    def ladderLength(self, beginWord: str, endWord: str, wordList: List[str]) -> int:
        """
        Interview explanation:
        Unweighted shortest path in the word graph (edges between words that
        differ by one letter). BFS from beginWord yields the shortest ladder
        length, counting words including begin and end.

        Algorithm:
        - Put dictionary in a set for O(1) membership.
        - BFS; for each word generate all one-letter mutations.
        - When a mutation is in the set, enqueue it and remove it (visited).
        - Return steps when endWord is reached; else 0.

        Complexity: O(N * L^2) time, O(N * L) space (N words, length L).
        """
        words: Set[str] = set(wordList)
        if endWord not in words:
            return 0

        queue = deque([(beginWord, 1)])
        words.discard(beginWord)

        while queue:
            word, steps = queue.popleft()
            if word == endWord:
                return steps
            chars = list(word)
            for i in range(len(chars)):
                original = chars[i]
                for c in "abcdefghijklmnopqrstuvwxyz":
                    if c == original:
                        continue
                    chars[i] = c
                    nxt = "".join(chars)
                    if nxt in words:
                        words.remove(nxt)
                        queue.append((nxt, steps + 1))
                chars[i] = original
        return 0

    def ladderLength_bidirectional(
        self, beginWord: str, endWord: str, wordList: List[str]
    ) -> int:
        """
        Interview explanation:
        Alternate best: bidirectional BFS meets in the middle, shrinking the
        explored frontier when the graph fans out.

        Algorithm:
        - Maintain two frontiers (begin side / end side) as sets.
        - Always expand the smaller frontier; generate neighbors.
        - If a neighbor is in the opposite frontier, return length.
        - Move visited words out of the dictionary set.

        Complexity: O(N * L^2) worst case, often much faster in practice; O(N * L) space.
        """
        words: Set[str] = set(wordList)
        if endWord not in words:
            return 0

        begin_front = {beginWord}
        end_front = {endWord}
        words.discard(beginWord)
        words.discard(endWord)
        length = 1

        while begin_front and end_front:
            if len(begin_front) > len(end_front):
                begin_front, end_front = end_front, begin_front

            next_front: Set[str] = set()
            for word in begin_front:
                chars = list(word)
                for i in range(len(chars)):
                    original = chars[i]
                    for c in "abcdefghijklmnopqrstuvwxyz":
                        if c == original:
                            continue
                        chars[i] = c
                        nxt = "".join(chars)
                        if nxt in end_front:
                            return length + 1
                        if nxt in words:
                            words.remove(nxt)
                            next_front.add(nxt)
                    chars[i] = original
            begin_front = next_front
            length += 1
        return 0
# @lc code=end
