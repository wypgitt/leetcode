#
# @lc app=leetcode id=1705 lang=python3
#
# [1705] Maximum Number of Eaten Apples
#
# https://leetcode.com/problems/maximum-number-of-eaten-apples/description/
#
# algorithms
# Medium (43.91%)
# Likes:    895
# Dislikes: 202
# Total Accepted:    35.5K
# Total Submissions: 80.8K
# Testcase Example:  "[1,2,3,5,2]"
#
# There is a special kind of apple tree that grows apples every day for n days.
# On the i^th day, the tree grows apples[i] apples that will rot after days[i]
# days, that is on day i + days[i] the apples will be rotten and cannot be
# eaten. On some days, the apple tree does not grow any apples, which are
# denoted by apples[i] == 0 and days[i] == 0.
#
# You decided to eat at most one apple a day (to keep the doctors away). Note
# that you can keep eating after the first n days.
#
# Given two integer arrays days and apples of length n, return the maximum
# number of apples you can eat.
#
# Example 1:
#
# Input: apples = [1,2,3,5,2], days = [3,2,1,4,2]
# Output: 7
# Explanation: You can eat 7 apples:
# - On the first day, you eat an apple that grew on the first day.
# - On the second day, you eat an apple that grew on the second day.
# - On the third day, you eat an apple that grew on the second day. After this
# day, the apples that grew on the third day rot.
# - On the fourth to the seventh days, you eat apples that grew on the fourth
# day.
#
# Example 2:
#
# Input: apples = [3,0,0,0,0,2], days = [3,0,0,0,0,2]
# Output: 5
# Explanation: You can eat 5 apples:
# - On the first to the third day you eat apples that grew on the first day.
# - Do nothing on the fouth and fifth days.
# - On the sixth and seventh days you eat apples that grew on the sixth day.
#
# Constraints:
#
# n == apples.length == days.length
#
# 1 <= n <= 2 * 10^4
#
# 0 <= apples[i], days[i] <= 2 * 10^4
#
# days[i] = 0 if and only if apples[i] = 0.
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def eatenApples(self, apples: List[int], days: List[int]) -> int:
        """
        Interview explanation:
        Each day i produces apples[i] that expire after days[i] days. Eat one apple
        per day preferring soonest-expiring batch (min-heap of (expiry, count)).

        Algorithm:
        - Day d from 0 while there are future harvests or leftover apples.
        - Add (d + days[d], apples[d]) if producing.
        - Pop expired; eat one from earliest expiry; push remainder.

        Complexity: O((n+A) log n) time, O(n) space.
        """
        n = len(apples)
        h = []
        eaten = 0
        d = 0
        while d < n or h:
            if d < n and apples[d]:
                heapq.heappush(h, [d + days[d], apples[d]])
            while h and (h[0][0] <= d or h[0][1] == 0):
                heapq.heappop(h)
            if h:
                h[0][1] -= 1
                eaten += 1
                if h[0][1] == 0:
                    heapq.heappop(h)
            d += 1
            if d >= n and not h:
                break
        return eaten
# @lc code=end
