#
# @lc app=leetcode id=3081 lang=python3
#
# [3081] Replace Question Marks in String to Minimize Its Value
#
# https://leetcode.com/problems/replace-question-marks-in-string-to-minimize-its-value/description/
#
# algorithms
# Medium (29.23%)
# Likes:    206
# Dislikes: 33
# Total Accepted:    18.5K
# Total Submissions: 63.3K
# Testcase Example:  "\"???\""
#
#
# You are given a string s. s[i] is either a lowercase English letter or
# '?'.
#
# For a string t having length m containing only lowercase English
# letters, we define the function cost(i) for an index i as the number of
# characters equal to t[i] that appeared before it, i.e. in the range [0,
# i - 1].
#
# The value of t is the sum of cost(i) for all indices i.
#
# For example, for the string t = "aab":
#
# cost(0) = 0
#
# cost(1) = 1
#
# cost(2) = 0
#
# Hence, the value of "aab" is 0 + 1 + 0 = 1.
#
# Your task is to replace all occurrences of '?' in s with any lowercase
# English letter so that the value of s is minimized.
#
# Return a string denoting the modified string with replaced occurrences
# of '?'. If there are multiple strings resulting in the minimum value,
# return the lexicographically smallest one.
#
# Example 1:
#
# Input:   s = "???"
#
# Output:   "abc"
#
# Explanation:  In this example, we can replace the occurrences of '?' to
# make s equal to "abc".
#
# For "abc", cost(0) = 0, cost(1) = 0, and cost(2) = 0.
#
# The value of "abc" is 0.
#
# Some other modifications of s that have a value of 0 are "cba", "abz",
# and, "hey".
#
# Among all of them, we choose the lexicographically smallest.
#
# Example 2:
#
# Input:  s = "a?a?"
#
# Output:  "abac"
#
# Explanation:  In this example, the occurrences of '?' can be replaced to
# make s equal to "abac".
#
# For "abac", cost(0) = 0, cost(1) = 0, cost(2) = 1, and cost(3) = 0.
#
# The value of "abac" is 1.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s[i] is either a lowercase English letter or '?'.
#

# @lc code=start
import heapq
from collections import Counter


class Solution:
    def minimizeStringValue(self, s: str) -> str:
        """
        Interview explanation:
        String value equals sum_c freq[c]*(freq[c]-1)/2, so only final letter
        frequencies matter. Assign each '?' to the currently rarest letter,
        then place those assigned letters into '?' slots in sorted order for
        the lexicographically smallest string.

        Algorithm:
        - Count fixed letters; min-heap of (freq, letter). For each '?', pop,
          record letter, push freq+1. Sort recorded letters and fill '?' left
          to right.

        Complexity: O(n log 26) time, O(n) space.
        """
        freq = Counter(ch for ch in s if ch != "?")
        heap = [(freq.get(chr(ord("a") + i), 0), chr(ord("a") + i)) for i in range(26)]
        heapq.heapify(heap)
        assigned = []
        for ch in s:
            if ch == "?":
                f, c = heapq.heappop(heap)
                assigned.append(c)
                heapq.heappush(heap, (f + 1, c))
        assigned.sort()
        it = iter(assigned)
        return "".join(next(it) if ch == "?" else ch for ch in s)
# @lc code=end
