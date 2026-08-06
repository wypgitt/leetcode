#
# @lc app=leetcode id=2594 lang=python3
#
# [2594] Minimum Time to Repair Cars
#
# https://leetcode.com/problems/minimum-time-to-repair-cars/description/
#
# algorithms
# Medium (59.49%)
# Likes:    1375
# Dislikes: 94
# Total Accepted:    158.6K
# Total Submissions: 266.5K
# Testcase Example:  "[4,2,3,1]\n10"
#
# You are given an integer array ranks representing the ranks of some mechanics.
# ranks_i is the rank of the i^th mechanic. A mechanic with a rank r can repair
# n cars in r * n^2 minutes.
#
# You are also given an integer cars representing the total number of cars
# waiting in the garage to be repaired.
#
# Return the minimum time taken to repair all the cars.
#
# Note: All the mechanics can repair the cars simultaneously.
#
#
#
# Example 1:
#
# Input: ranks = [4,2,3,1], cars = 10
# Output: 16
# Explanation:
# - The first mechanic will repair two cars. The time required is 4 * 2 * 2 = 16
# minutes.
# - The second mechanic will repair two cars. The time required is 2 * 2 * 2 = 8
# minutes.
# - The third mechanic will repair two cars. The time required is 3 * 2 * 2 = 12
# minutes.
# - The fourth mechanic will repair four cars. The time required is 1 * 4 * 4 =
# 16 minutes.
# It can be proved that the cars cannot be repaired in less than 16
# minutes.​​​​​
#
# Example 2:
#
# Input: ranks = [5,1,8], cars = 6
# Output: 16
# Explanation:
# - The first mechanic will repair one car. The time required is 5 * 1 * 1 = 5
# minutes.
# - The second mechanic will repair four cars. The time required is 1 * 4 * 4 =
# 16 minutes.
# - The third mechanic will repair one car. The time required is 8 * 1 * 1 = 8
# minutes.
# It can be proved that the cars cannot be repaired in less than 16
# minutes.​​​​​
#
#
#
# Constraints:
#
#
# 1 <= ranks.length <= 10^5
#
#
# 1 <= ranks[i] <= 100
#
#
# 1 <= cars <= 10^6
#

# @lc code=start
from typing import List
import math


class Solution:
    def repairCars(self, ranks: List[int], cars: int) -> int:
        """
        Interview explanation:
        Mechanic with rank r repairs n cars in r*n^2 minutes. Minimize time to repair
        all cars (parallel mechanics).

        Algorithm:
        - Binary search time T; each mechanic repairs floor(sqrt(T/r)) cars.

        Complexity: O(m log(max_r * cars^2)) time, O(1) space.
        """
        lo, hi = 1, min(ranks) * cars * cars

        def ok(t: int) -> bool:
            total = 0
            for r in ranks:
                total += int(math.isqrt(t // r))
                if total >= cars:
                    return True
            return False

        while lo < hi:
            mid = (lo + hi) // 2
            if ok(mid):
                hi = mid
            else:
                lo = mid + 1
        return lo
# @lc code=end
