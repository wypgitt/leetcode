#
# @lc app=leetcode id=3093 lang=python3
#
# [3093] Longest Common Suffix Queries
#
# https://leetcode.com/problems/longest-common-suffix-queries/description/
#
# algorithms
# Hard (52.63%)
# Likes:    439
# Dislikes: 35
# Total Accepted:    81.2K
# Total Submissions: 154.3K
# Testcase Example:  "[\"abcd\",\"bcd\",\"xbcd\"]\n[\"cd\",\"bcd\",\"xyz\"]"
#
#
# You are given two arrays of strings wordsContainer and wordsQuery.
#
# For each wordsQuery[i], you need to find a string from wordsContainer
# that has the longest common suffix with wordsQuery[i]. If there are two
# or more strings in wordsContainer that share the longest common suffix,
# find the string that is the smallest in length. If there are two or more
# such strings that have the same smallest length, find the one that
# occurred earlier in wordsContainer.
#
# Return an array of integers ans, where ans[i] is the index of the string
# in wordsContainer that has the longest common suffix with wordsQuery[i].
#
# Example 1:
#
# Input: wordsContainer = ["abcd","bcd","xbcd"], wordsQuery =
# ["cd","bcd","xyz"]
#
# Output: [1,1,1]
#
# Explanation:
#
# Let's look at each wordsQuery[i] separately:
#
# For wordsQuery[0] = "cd", strings from wordsContainer that share the
# longest common suffix "cd" are at indices 0, 1, and 2. Among these, the
# answer is the string at index 1 because it has the shortest length of 3.
#
# For wordsQuery[1] = "bcd", strings from wordsContainer that share the
# longest common suffix "bcd" are at indices 0, 1, and 2. Among these, the
# answer is the string at index 1 because it has the shortest length of 3.
#
# For wordsQuery[2] = "xyz", there is no string from wordsContainer that
# shares a common suffix. Hence the longest common suffix is "", that is
# shared with strings at index 0, 1, and 2. Among these, the answer is the
# string at index 1 because it has the shortest length of 3.
#
# Example 2:
#
# Input: wordsContainer = ["abcdefgh","poiuygh","ghghgh"], wordsQuery =
# ["gh","acbfgh","acbfegh"]
#
# Output: [2,0,2]
#
# Explanation:
#
# Let's look at each wordsQuery[i] separately:
#
# For wordsQuery[0] = "gh", strings from wordsContainer that share the
# longest common suffix "gh" are at indices 0, 1, and 2. Among these, the
# answer is the string at index 2 because it has the shortest length of 6.
#
# For wordsQuery[1] = "acbfgh", only the string at index 0 shares the
# longest common suffix "fgh". Hence it is the answer, even though the
# string at index 2 is shorter.
#
# For wordsQuery[2] = "acbfegh", strings from wordsContainer that share
# the longest common suffix "gh" are at indices 0, 1, and 2. Among these,
# the answer is the string at index 2 because it has the shortest length
# of 6.
#
# Constraints:
#
# 1 <= wordsContainer.length, wordsQuery.length <= 10^4
#
# 1 <= wordsContainer[i].length <= 5 * 10^3
#
# 1 <= wordsQuery[i].length <= 5 * 10^3
#
# wordsContainer[i] consists only of lowercase English letters.
#
# wordsQuery[i] consists only of lowercase English letters.
#
# Sum of wordsContainer[i].length is at most 5 * 10^5.
#
# Sum of wordsQuery[i].length is at most 5 * 10^5.
#

# @lc code=start
from typing import List


class Solution:
    def stringIndices(self, wordsContainer: List[str], wordsQuery: List[str]) -> List[int]:
        """
        Interview explanation:
        For each query, pick the container word with longest common suffix;
        break ties by shortest length, then earliest index.

        Algorithm:
        - Trie on reversed words; each node stores best (shortest, earliest) word
          reaching that suffix. Walk query reversed; last matching node wins
          (root covers empty common suffix).

        Complexity: O(total length) time and space.
        """
        class Node:
            __slots__ = ("ch", "best_i", "best_len")

            def __init__(self):
                self.ch = {}
                self.best_i = -1
                self.best_len = 10**9

        root = Node()
        for i, w in enumerate(wordsContainer):
            if len(w) < root.best_len:
                root.best_len = len(w)
                root.best_i = i
            node = root
            for c in reversed(w):
                if c not in node.ch:
                    node.ch[c] = Node()
                node = node.ch[c]
                if len(w) < node.best_len:
                    node.best_len = len(w)
                    node.best_i = i

        ans = []
        for q in wordsQuery:
            node = root
            best = root.best_i
            for c in reversed(q):
                if c not in node.ch:
                    break
                node = node.ch[c]
                best = node.best_i
            ans.append(best)
        return ans
# @lc code=end
