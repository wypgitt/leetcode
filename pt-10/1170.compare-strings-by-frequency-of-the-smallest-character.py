#
# @lc app=leetcode id=1170 lang=python3
#
# [1170] Compare Strings by Frequency of the Smallest Character
#
# https://leetcode.com/problems/compare-strings-by-frequency-of-the-smallest-character/description/
#
# algorithms
# Medium (63.52%)
# Likes:    759
# Dislikes: 982
# Total Accepted:    94.9K
# Total Submissions: 149K
# Testcase Example:  "[\"cbd\"]"
#
# Let the function f(s) be the frequency of the lexicographically smallest
# character in a non-empty string s. For example, if s = "dcce" then f(s) = 2
# because the lexicographically smallest character is 'c', which has a
# frequency of 2.
#
# You are given an array of strings words and another array of query strings
# queries. For each query queries[i], count the number of words in words such
# that f(queries[i]) < f(W) for each W in words.
#
# Return an integer array answer, where each answer[i] is the answer to the
# i^th query.
#
# Example 1:
#
# Input: queries = ["cbd"], words = ["zaaaz"]
# Output: [1]
# Explanation: On the first query we have f("cbd") = 1, f("zaaaz") = 3 so
# f("cbd") < f("zaaaz").
#
# Example 2:
#
# Input: queries = ["bbb","cc"], words = ["a","aa","aaa","aaaa"]
# Output: [1,2]
# Explanation: On the first query only f("bbb") < f("aaaa"). On the second
# query both f("aaa") and f("aaaa") are both > f("cc").
#
# Constraints:
#
# 1 <= queries.length <= 2000
#
# 1 <= words.length <= 2000
#
# 1 <= queries[i].length, words[i].length <= 10
#
# queries[i][j], words[i][j] consist of lowercase English letters.
#

# @lc code=start

import bisect
from typing import List


class Solution:
    def numSmallerByFrequency(self, queries: List[str], words: List[str]) -> List[int]:
        """
        Interview explanation:
        f(s) = count of the lexicographically smallest char in s. Precompute
        f(words), sort them, and for each query binary-search how many words
        have strictly greater f.

        Algorithm (sort + binary search):
        - freqs = sorted(f(w) for w in words).
        - For query q with x=f(q): answer = n - bisect_right(freqs, x).

        Complexity: O((n+m) L + n log n + m log n) time, O(n) space.
        """
        def f(s: str) -> int:
            return s.count(min(s))

        freqs = sorted(f(w) for w in words)
        n = len(freqs)
        return [n - bisect.bisect_right(freqs, f(q)) for q in queries]

    def numSmallerByFrequency_counting(self, queries: List[str], words: List[str]) -> List[int]:
        """
        Interview explanation:
        Alternate: f values are at most 10 (word length ≤ 10). Count frequencies
        and use a suffix array for O(1) queries after O(n) prep.

        Algorithm:
        - cnt[f]++ for each word.
        - greater[x] = sum(cnt[x+1..]); answer greater[f(q)].

        Complexity: O((n+m) L) time, O(1) extra (fixed buckets).
        """
        def f(s: str) -> int:
            return s.count(min(s))

        cnt = [0] * 12
        for w in words:
            cnt[f(w)] += 1
        greater = [0] * 12
        running = 0
        for x in range(11, -1, -1):
            greater[x] = running
            running += cnt[x]
        return [greater[f(q)] for q in queries]
# @lc code=end
