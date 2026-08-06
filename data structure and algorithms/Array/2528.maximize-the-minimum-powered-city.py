#
# @lc app=leetcode id=2528 lang=python3
#
# [2528] Maximize the Minimum Powered City
#
# https://leetcode.com/problems/maximize-the-minimum-powered-city/description/
#
# algorithms
# Hard (61.44%)
# Likes:    884
# Dislikes: 33
# Total Accepted:    69.3K
# Total Submissions: 112.8K
# Testcase Example:  "[1,2,4,5,0]\n1\n2"
#
# You are given a 0-indexed integer array stations of length n, where
# stations[i] represents the number of power stations in the i^th city.
#
# Each power station can provide power to every city in a fixed range. In other
# words, if the range is denoted by r, then a power station at city i can
# provide power to all cities j such that |i - j| <= r and 0 <= i, j <= n - 1.
#
#
# Note that |x| denotes absolute value. For example, |7 - 5| = 2 and |3 - 10| =
# 7.
#
# The power of a city is the total number of power stations it is being provided
# power from.
#
# The government has sanctioned building k more power stations, each of which
# can be built in any city, and have the same range as the pre-existing ones.
#
# Given the two integers r and k, return the maximum possible minimum power of a
# city, if the additional power stations are built optimally.
#
# Note that you can build the k power stations in multiple cities.
#
#
#
# Example 1:
#
# Input: stations = [1,2,4,5,0], r = 1, k = 2
# Output: 5
# Explanation:
# One of the optimal ways is to install both the power stations at city 1.
# So stations will become [1,4,4,5,0].
# - City 0 is provided by 1 + 4 = 5 power stations.
# - City 1 is provided by 1 + 4 + 4 = 9 power stations.
# - City 2 is provided by 4 + 4 + 5 = 13 power stations.
# - City 3 is provided by 5 + 4 = 9 power stations.
# - City 4 is provided by 5 + 0 = 5 power stations.
# So the minimum power of a city is 5.
# Since it is not possible to obtain a larger power, we return 5.
#
# Example 2:
#
# Input: stations = [4,4,4,4], r = 0, k = 3
# Output: 4
# Explanation:
# It can be proved that we cannot make the minimum power of a city greater than
# 4.
#
#
#
# Constraints:
#
#
# n == stations.length
#
#
# 1 <= n <= 10^5
#
#
# 0 <= stations[i] <= 10^5
#
#
# 0 <= r <= n - 1
#
#
# 0 <= k <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def maxPower(self, stations: List[int], r: int, k: int) -> int:
        """
        Interview explanation:
        Each station powers cities within distance r. Add at most k stations
        to maximize the minimum city power.

        Algorithm:
        - Prefix-sum initial powers. Binary search answer mid; check with a
          difference array: scan left->right, when city i is short, place the
          deficit at i+r (covers farthest right) and record via diff.

        Complexity: O(n log (sum(stations)+k)) time, O(n) space.
        """
        n = len(stations)
        pref = [0] * (n + 1)
        for i, x in enumerate(stations):
            pref[i + 1] = pref[i] + x
        power = [0] * n
        for i in range(n):
            L = max(0, i - r)
            R = min(n - 1, i + r)
            power[i] = pref[R + 1] - pref[L]

        def can(mid: int) -> bool:
            diff = [0] * n
            add = 0
            used = 0
            for i in range(n):
                add += diff[i]
                cur = power[i] + add
                if cur < mid:
                    need = mid - cur
                    used += need
                    if used > k:
                        return False
                    add += need
                    end = i + 2 * r + 1
                    if end < n:
                        diff[end] -= need
            return True

        lo, hi = 0, max(power) + k
        ans = 0
        while lo <= hi:
            mid = (lo + hi) // 2
            if can(mid):
                ans = mid
                lo = mid + 1
            else:
                hi = mid - 1
        return ans
# @lc code=end
