#
# @lc app=leetcode id=2247 lang=python3
#
# [2247] Maximum Cost of Trip With K Highways
#
# https://leetcode.com/problems/maximum-cost-of-trip-with-k-highways/description/
#
# algorithms
# Hard (50.62%)
# Likes:    63
# Dislikes: 0
# Total Accepted:    2.5K
# Total Submissions: 4.9K
# Testcase Example:  "5\n[[0,1,4],[2,1,3],[1,4,11],[3,2,3],[3,4,2]]\n3"
#
#
# A series of highways connect n cities numbered from 0 to n - 1. You are
# given a 2D integer array highways where highways[i] = [city1_i, city2_i,
# toll_i] indicates that there is a highway that connects city1_i and
# city2_i, allowing a car to go from city1_i to city2_i and vice versa for
# a cost of toll_i.
#
# You are also given an integer k. You are going on a trip that crosses
# exactly k highways. You may start at any city, but you may only visit
# each city at most once during your trip.
#
# Return the maximum cost of your trip. If there is no trip that meets the
# requirements, return -1.
#
# Example 1:
#
# Input: n = 5, highways = [[0,1,4],[2,1,3],[1,4,11],[3,2,3],[3,4,2]], k =
# 3
# Output: 17
# Explanation:
# One possible trip is to go from 0 -> 1 -> 4 -> 3. The cost of this trip
# is 4 + 11 + 2 = 17.
# Another possible trip is to go from 4 -> 1 -> 2 -> 3. The cost of this
# trip is 11 + 3 + 3 = 17.
# It can be proven that 17 is the maximum possible cost of any valid trip.
#
# Note that the trip 4 -> 1 -> 0 -> 1 is not allowed because you visit the
# city 1 twice.
#
# Example 2:
#
# Input: n = 4, highways = [[0,1,3],[2,3,2]], k = 2
# Output: -1
# Explanation: There are no valid trips of length 2, so return -1.
#
# Constraints:
#
# 2 <= n <= 15
#
# 1 <= highways.length <= 50
#
# highways[i].length == 3
#
# 0 <= city1_i, city2_i <= n - 1
#
# city1_i != city2_i
#
# 0 <= toll_i <= 100
#
# 1 <= k <= 50
#
# There are no duplicate highways.
#
# @lc code=start
from typing import List
from functools import lru_cache


class Solution:
    def maximumCost(self, n: int, highways: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Premium. Undirected highways with tolls. Trip of exactly k highways visits
        k+1 distinct cities; cost = sum of tolls. Max cost or -1.

        Algorithm:
        (bitmask DP)
        - n<=15: dp(u, mask) = max remaining toll sum to reach k+1 cities from u
          with visited mask. Try all starts.

        Complexity: O(n^2 * 2^n) time, O(n * 2^n) space.
        """
        if k >= n:
            return -1
        g = [[] for _ in range(n)]
        for u, v, w in highways:
            g[u].append((v, w))
            g[v].append((u, w))

        @lru_cache(None)
        def dp(u: int, mask: int) -> int:
            if mask.bit_count() == k + 1:
                return 0
            res = -1
            for v, w in g[u]:
                if mask >> v & 1:
                    continue
                nxt = dp(v, mask | (1 << v))
                if nxt != -1:
                    res = max(res, w + nxt)
            return res

        ans = max(dp(i, 1 << i) for i in range(n))
        return ans
# @lc code=end
