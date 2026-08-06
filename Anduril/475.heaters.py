#
# @lc app=leetcode id=475 lang=python3
#
# [475] Heaters
#
# https://leetcode.com/problems/heaters/description/
#
# algorithms
# Medium (42.39%)
# Likes:    2393
# Dislikes: 1201
# Total Accepted:    179K
# Total Submissions: 423K
# Testcase Example:  "[1,2,3]"
#
# Winter is coming! During the contest, your first job is to design a standard
# heater with a fixed warm radius to warm all the houses.
#
# Every house can be warmed, as long as the house is within the heater's warm
# radius range.
#
# Given the positions of houses and heaters on a horizontal line, return the
# minimum radius standard of heaters so that those heaters could cover all
# houses.
#
# Notice that all the heaters follow your radius standard, and the warm radius
# will be the same.
#
# Example 1:
#
# Input: houses = [1,2,3], heaters = [2]
# Output: 1
# Explanation: The only heater was placed in the position 2, and if we use the
# radius 1 standard, then all the houses can be warmed.
#
# Example 2:
#
# Input: houses = [1,2,3,4], heaters = [1,4]
# Output: 1
# Explanation: The two heaters were placed at positions 1 and 4. We need to use
# a radius 1 standard, then all the houses can be warmed.
#
# Example 3:
#
# Input: houses = [1,5], heaters = [2]
# Output: 3
#
# Constraints:
#
# 1 <= houses.length, heaters.length <= 3 * 10^4
#
# 1 <= houses[i], heaters[i] <= 10^9
#

# @lc code=start
from bisect import bisect_left
from typing import List


class Solution:
    def findRadius(self, houses: List[int], heaters: List[int]) -> int:
        """
        Interview explanation:
        Binary search nearest heater for each house (or two-pointer after sort).
        Radius needed = max over houses of min distance to a heater.

        Algorithm:
        - Sort heaters.
        - For each house, bisect to find insertion point; dist = min to
          heaters[i-1] and heaters[i] if exist.
        - Answer = max of those distances.

        Complexity: O((n+m) log m) time, O(1)/O(m) space.
        """
        heaters.sort()
        ans = 0
        for h in houses:
            i = bisect_left(heaters, h)
            dist = float("inf")
            if i < len(heaters):
                dist = min(dist, heaters[i] - h)
            if i > 0:
                dist = min(dist, h - heaters[i - 1])
            ans = max(ans, dist)
        return int(ans)

    def findRadius_two_pointers(self, houses: List[int], heaters: List[int]) -> int:
        """
        Interview explanation:
        Alternate classic: sort both arrays; two-pointer advances the heater
        index while the next heater is closer than the current one.

        Algorithm:
        - Sort houses and heaters; j = 0.
        - For each house: while j+1 < m and heaters[j+1] closer, j++.
          ans = max(ans, |house - heaters[j]|).

        Complexity: O(n log n + m log m) time, O(1)/O(n+m) space.
        """
        houses = sorted(houses)
        heaters = sorted(heaters)
        ans = j = 0
        m = len(heaters)
        for h in houses:
            while j + 1 < m and abs(heaters[j + 1] - h) <= abs(heaters[j] - h):
                j += 1
            ans = max(ans, abs(heaters[j] - h))
        return ans
# @lc code=end
