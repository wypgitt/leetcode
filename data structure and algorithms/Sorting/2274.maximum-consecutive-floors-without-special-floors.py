#
# @lc app=leetcode id=2274 lang=python3
#
# [2274] Maximum Consecutive Floors Without Special Floors
#
# https://leetcode.com/problems/maximum-consecutive-floors-without-special-floors/description/
#
# algorithms
# Medium (52.76%)
# Likes:    433
# Dislikes: 41
# Total Accepted:    44.1K
# Total Submissions: 83.6K
# Testcase Example:  "2\n9\n[4,6]"
#
# Alice manages a company and has rented some floors of a building as office
# space. Alice has decided some of these floors should be special floors, used
# for relaxation only.
#
# You are given two integers bottom and top, which denote that Alice has rented
# all the floors from bottom to top (inclusive). You are also given the integer
# array special, where special[i] denotes a special floor that Alice has
# designated for relaxation.
#
# Return the maximum number of consecutive floors without a special floor.
#
#
#
# Example 1:
#
# Input: bottom = 2, top = 9, special = [4,6]
# Output: 3
# Explanation: The following are the ranges (inclusive) of consecutive floors
# without a special floor:
# - (2, 3) with a total amount of 2 floors.
# - (5, 5) with a total amount of 1 floor.
# - (7, 9) with a total amount of 3 floors.
# Therefore, we return the maximum number which is 3 floors.
#
# Example 2:
#
# Input: bottom = 6, top = 8, special = [7,6,8]
# Output: 0
# Explanation: Every floor rented is a special floor, so we return 0.
#
#
#
# Constraints:
#
#
# 1 <= special.length <= 10^5
#
#
# 1 <= bottom <= special[i] <= top <= 10^9
#
#
# All the values of special are unique.
#

# @lc code=start
from typing import List


class Solution:
    def maxConsecutive(self, bottom: int, top: int, special: List[int]) -> int:
        """
        Interview explanation:
        Max consecutive floors in [bottom, top] containing no special floors.

        Algorithm:
        - Sort special; max gaps between consecutive specials and ends.

        Complexity: O(s log s) time, O(1) extra space.
        """
        special.sort()
        ans = max(special[0] - bottom, top - special[-1])
        for i in range(1, len(special)):
            ans = max(ans, special[i] - special[i - 1] - 1)
        return ans
# @lc code=end
