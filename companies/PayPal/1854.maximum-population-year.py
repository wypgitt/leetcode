#
# @lc app=leetcode id=1854 lang=python3
#
# [1854] Maximum Population Year
#
# https://leetcode.com/problems/maximum-population-year/description/
#
# algorithms
# Easy (64.46%)
# Likes:    1578
# Dislikes: 294
# Total Accepted:    125K
# Total Submissions: 194K
# Testcase Example:  "[[1993,1999],[2000,2010]]"
#
# You are given a 2D integer array logs where each logs[i] = [birth_i, death_i]
# indicates the birth and death years of the i^th person.
#
# The population of some year x is the number of people alive during that year.
# The i^th person is counted in year x's population if x is in the inclusive
# range [birth_i, death_i - 1]. Note that the person is not counted in the year
# that they die.
#
# Return the earliest year with the maximum population.
#
# Example 1:
#
# Input: logs = [[1993,1999],[2000,2010]]
# Output: 1993
# Explanation: The maximum population is 1, and 1993 is the earliest year with
# this population.
#
# Example 2:
#
# Input: logs = [[1950,1961],[1960,1971],[1970,1981]]
# Output: 1960
# Explanation:
# The maximum population is 2, and it had happened in years 1960 and 1970.
# The earlier year between them is 1960.
#
# Constraints:
#
# 1 <= logs.length <= 100
#
# 1950 <= birth_i < death_i <= 2050
#

# @lc code=start
from typing import List


class Solution:
    def maximumPopulation(self, logs: List[List[int]]) -> int:
        """
        Interview explanation:
        Population in [birth, death) years. Find earliest year with max live count.
        Difference array over years 1950..2050.

        Algorithm (sweep / diff array):
        - diff[b]++, diff[d]--; prefix sum; track max and year.

        Complexity: O(n + Y) time, O(Y) space (Y≈100).
        """
        diff = [0] * 101
        for b, d in logs:
            diff[b - 1950] += 1
            diff[d - 1950] -= 1
        best = cur = year = 0
        for i, d in enumerate(diff):
            cur += d
            if cur > best:
                best = cur
                year = i
        return 1950 + year

    def maximumPopulation_bruteforce(self, logs: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: for each year 1950..2050 count how many people alive.

        Algorithm:
        - For y in range: count births≤y <deaths; track max.

        Complexity: O(n*Y) time.
        """
        best = year = 0
        for y in range(1950, 2051):
            cur = sum(1 for b, d in logs if b <= y < d)
            if cur > best:
                best = cur
                year = y
        return year
# @lc code=end
