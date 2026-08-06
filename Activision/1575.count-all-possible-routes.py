#
# @lc app=leetcode id=1575 lang=python3
#
# [1575] Count All Possible Routes
#
# https://leetcode.com/problems/count-all-possible-routes/description/
#
# algorithms
# Hard (64.76%)
# Likes:    1694
# Dislikes: 60
# Total Accepted:    67.6K
# Total Submissions: 104K
# Testcase Example:  "[2,3,6,8,4]"
#
# You are given an array of distinct positive integers locations where
# locations[i] represents the position of city i. You are also given integers
# start, finish and fuel representing the starting city, ending city, and the
# initial amount of fuel you have, respectively.
#
# At each step, if you are at city i, you can pick any city j such that j != i
# and 0 <= j < locations.length and move to city j. Moving from city i to city
# j reduces the amount of fuel you have by |locations[i] - locations[j]|.
# Please notice that |x| denotes the absolute value of x.
#
# Notice that fuel cannot become negative at any point in time, and that you
# are allowed to visit any city more than once (including start and finish).
#
# Return the count of all possible routes from start to finish. Since the
# answer may be too large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: locations = [2,3,6,8,4], start = 1, finish = 3, fuel = 5
# Output: 4
# Explanation: The following are all possible routes, each uses 5 units of
# fuel:
# 1 -> 3
# 1 -> 2 -> 3
# 1 -> 4 -> 3
# 1 -> 4 -> 2 -> 3
#
# Example 2:
#
# Input: locations = [4,3,1], start = 1, finish = 0, fuel = 6
# Output: 5
# Explanation: The following are all possible routes:
# 1 -> 0, used fuel = 1
# 1 -> 2 -> 0, used fuel = 5
# 1 -> 2 -> 1 -> 0, used fuel = 5
# 1 -> 0 -> 1 -> 0, used fuel = 3
# 1 -> 0 -> 1 -> 0 -> 1 -> 0, used fuel = 5
#
# Example 3:
#
# Input: locations = [5,2,1], start = 0, finish = 2, fuel = 3
# Output: 0
# Explanation: It is impossible to get from 0 to 2 using only 3 units of fuel
# since the shortest route needs 4 units of fuel.
#
# Constraints:
#
# 2 <= locations.length <= 100
#
# 1 <= locations[i] <= 10^9
#
# All integers in locations are distinct.
#
# 0 <= start, finish < locations.length
#
# 1 <= fuel <= 200
#

# @lc code=start
from typing import List
from functools import lru_cache


class Solution:
    def countRoutes(self, locations: List[int], start: int, finish: int, fuel: int) -> int:
        """
        Interview explanation:
        Count routes from start to finish with fuel cost = |loc[i]-loc[j]| per
        hop; can visit any city any times including finish mid-route. Memo DP
        on (city, remaining fuel); from city try all other cities if cost<=fuel.

        Algorithm (top-down DP):
        - dp(i,f)= (1 if i==finish else 0) + sum dp(j, f-|li-lj|) for j!=i if cost<=f
        - Mod 10^9+7.

        Complexity: O(n^2 * fuel) time/space.
        """
        MOD = 10**9 + 7
        n = len(locations)

        @lru_cache(None)
        def dp(i: int, f: int) -> int:
            ans = 1 if i == finish else 0
            for j in range(n):
                if j == i:
                    continue
                cost = abs(locations[i] - locations[j])
                if cost <= f:
                    ans = (ans + dp(j, f - cost)) % MOD
            return ans

        return dp(start, fuel)

    def countRoutes_bottomup(self, locations: List[int], start: int, finish: int, fuel: int) -> int:
        """
        Interview explanation:
        Alternate bottom-up: dp[f][i] ways to be at i with exactly f fuel used
        (or remaining). Iterate remaining fuel descending/ascending carefully.

        Algorithm:
        - dp[i][f] same recurrence iteratively for f from 0..fuel.

        Complexity: O(n^2 * fuel).
        """
        MOD = 10**9 + 7
        n = len(locations)
        dp = [[0] * (fuel + 1) for _ in range(n)]
        for f in range(fuel + 1):
            dp[finish][f] = 1
        for f in range(fuel + 1):
            for i in range(n):
                for j in range(n):
                    if i == j:
                        continue
                    cost = abs(locations[i] - locations[j])
                    if cost <= f:
                        dp[i][f] = (dp[i][f] + dp[j][f - cost]) % MOD
        return dp[start][fuel]
# @lc code=end

