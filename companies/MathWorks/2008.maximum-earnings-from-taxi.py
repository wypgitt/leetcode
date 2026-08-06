#
# @lc app=leetcode id=2008 lang=python3
#
# [2008] Maximum Earnings From Taxi
#
# https://leetcode.com/problems/maximum-earnings-from-taxi/description/
#
# algorithms
# Medium (46.69%)
# Likes:    1429
# Dislikes: 26
# Total Accepted:    51.8K
# Total Submissions: 110.9K
# Testcase Example:  "5\n[[2,5,4],[1,5,1]]"
#
# There are n points on a road you are driving your taxi on. The n points on the
# road are labeled from 1 to n in the direction you are going, and you want to
# drive from point 1 to point n to make money by picking up passengers. You
# cannot change the direction of the taxi.
#
# The passengers are represented by a 0-indexed 2D integer array rides, where
# rides[i] = [start_i, end_i, tip_i] denotes the i^th passenger requesting a
# ride from point start_i to point end_i who is willing to give a tip_i dollar
# tip.
#
# For each passenger i you pick up, you earn end_i - start_i + tip_i dollars.
# You may only drive at most one passenger at a time.
#
# Given n and rides, return the maximum number of dollars you can earn by
# picking up the passengers optimally.
#
# Note: You may drop off a passenger and pick up a different passenger at the
# same point.
#
#
#
# Example 1:
#
# Input: n = 5, rides = [[2,5,4],[1,5,1]]
# Output: 7
# Explanation: We can pick up passenger 0 to earn 5 - 2 + 4 = 7 dollars.
#
# Example 2:
#
# Input: n = 20, rides =
# [[1,6,1],[3,10,2],[10,12,3],[11,12,2],[12,15,2],[13,18,1]]
# Output: 20
# Explanation: We will pick up the following passengers:
# - Drive passenger 1 from point 3 to point 10 for a profit of 10 - 3 + 2 = 9
# dollars.
# - Drive passenger 2 from point 10 to point 12 for a profit of 12 - 10 + 3 = 5
# dollars.
# - Drive passenger 5 from point 13 to point 18 for a profit of 18 - 13 + 1 = 6
# dollars.
# We earn 9 + 5 + 6 = 20 dollars in total.
#
#
#
# Constraints:
#
#
# 1 <= n <= 10^5
#
#
# 1 <= rides.length <= 3 * 10^4
#
#
# rides[i].length == 3
#
#
# 1 <= start_i < end_i <= n
#
#
# 1 <= tip_i <= 10^5
#

# @lc code=start
from typing import List
from collections import defaultdict
import bisect


class Solution:
    def maxTaxiEarnings(self, n: int, rides: List[List[int]]) -> int:
        """
        Interview explanation:
        On a line 1..n, each ride [start,end,tip] earns end-start+tip; rides must
        not overlap. Maximize earnings (DP on ending point).

        Algorithm:
        - Group rides by end. dp[i] = max earn finishing at or before i.
        - dp[i] = max(dp[i-1], max over rides ending at i: dp[start]+profit).

        Complexity: O(n + m) time, O(n + m) space.
        """
        by_end = defaultdict(list)
        for s, e, tip in rides:
            by_end[e].append((s, e - s + tip))
        dp = [0] * (n + 1)
        for i in range(1, n + 1):
            dp[i] = dp[i - 1]
            for s, profit in by_end[i]:
                dp[i] = max(dp[i], dp[s] + profit)
        return dp[n]

    def maxTaxiEarnings_binary_search(self, n: int, rides: List[List[int]]) -> int:
        """
        Interview explanation:
        Classic alternate: sort rides by end; for each ride binary-search last
        non-overlapping ride and take max DP.

        Algorithm:
        - Sort by end; dp[i] = max(dp[i-1], profit[i]+dp[j]) where ends[j]<=start.

        Complexity: O(m log m) time, O(m) space.
        """
        rides = sorted(rides, key=lambda r: r[1])
        m = len(rides)
        ends = [r[1] for r in rides]
        dp = [0] * (m + 1)
        for i, (s, e, tip) in enumerate(rides, 1):
            j = bisect.bisect_right(ends, s, 0, i - 1)
            profit = e - s + tip
            dp[i] = max(dp[i - 1], dp[j] + profit)
        return dp[m]
# @lc code=end
