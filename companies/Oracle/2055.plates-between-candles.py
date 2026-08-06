#
# @lc app=leetcode id=2055 lang=python3
#
# [2055] Plates Between Candles
#
# https://leetcode.com/problems/plates-between-candles/description/
#
# algorithms
# Medium (47.67%)
# Likes:    1376
# Dislikes: 74
# Total Accepted:    79.8K
# Total Submissions: 167.4K
# Testcase Example:  "\"**|**|***|\"\n[[2,5],[5,9]]"
#
# There is a long table with a line of plates and candles arranged on top of it.
# You are given a 0-indexed string s consisting of characters '*' and '|' only,
# where a '*' represents a plate and a '|' represents a candle.
#
# You are also given a 0-indexed 2D integer array queries where queries[i] =
# [left_i, right_i] denotes the substring s[left_i...right_i] (inclusive). For
# each query, you need to find the number of plates between candles that are in
# the substring. A plate is considered between candles if there is at least one
# candle to its left and at least one candle to its right in the substring.
#
#
# For example, s = "||**||**|*", and a query [3, 8] denotes the substring
# "*||**|". The number of plates between candles in this substring is 2, as each
# of the two plates has at least one candle in the substring to its left and
# right.
#
# Return an integer array answer where answer[i] is the answer to the i^th
# query.
#
#
#
# Example 1:
#
# Input: s = "**|**|***|", queries = [[2,5],[5,9]]
# Output: [2,3]
# Explanation:
# - queries[0] has two plates between candles.
# - queries[1] has three plates between candles.
#
# Example 2:
#
# Input: s = "***|**|*****|**||**|*", queries =
# [[1,17],[4,5],[14,17],[5,11],[15,16]]
# Output: [9,0,0,0,0]
# Explanation:
# - queries[0] has nine plates between candles.
# - The other queries have zero plates between candles.
#
#
#
# Constraints:
#
#
# 3 <= s.length <= 10^5
#
#
# s consists of '*' and '|' characters.
#
#
# 1 <= queries.length <= 10^5
#
#
# queries[i].length == 2
#
#
# 0 <= left_i <= right_i < s.length
#

# @lc code=start
from typing import List
import bisect


class Solution:
    def platesBetweenCandles(self, s: str, queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        For each query [left,right], count '*' plates between the leftmost and
        rightmost '|' candles inside the substring.

        Algorithm:
        - pref plates; candles indices; find bounding candles; plates between.

        Complexity: O(n + q log n) time, O(n) space.
        """
        n = len(s)
        pref = [0] * (n + 1)
        candles = []
        for i, ch in enumerate(s):
            pref[i + 1] = pref[i] + (ch == '*')
            if ch == '|':
                candles.append(i)
        ans = []
        for left, right in queries:
            li = bisect.bisect_left(candles, left)
            ri = bisect.bisect_right(candles, right) - 1
            if li < ri:
                lc, rc = candles[li], candles[ri]
                ans.append(pref[rc] - pref[lc + 1])
            else:
                ans.append(0)
        return ans

    def platesBetweenCandles_nearest(self, s: str, queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Alternate O(n+q): nearest candle arrays to left/right of every index.

        Algorithm:
        - Precompute left[i]/right[i] nearest '|'; answer via plate prefix.

        Complexity: O(n + q) time, O(n) space.
        """
        n = len(s)
        pref = [0] * (n + 1)
        left = [-1] * n
        right = [-1] * n
        last = -1
        for i, ch in enumerate(s):
            pref[i + 1] = pref[i] + (ch == '*')
            if ch == '|':
                last = i
            left[i] = last
        last = -1
        for i in range(n - 1, -1, -1):
            if s[i] == '|':
                last = i
            right[i] = last
        ans = []
        for l, r in queries:
            lc, rc = right[l], left[r]
            if lc != -1 and rc != -1 and lc < rc:
                ans.append(pref[rc] - pref[lc + 1])
            else:
                ans.append(0)
        return ans
# @lc code=end
