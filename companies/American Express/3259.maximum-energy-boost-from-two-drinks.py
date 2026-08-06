#
# @lc app=leetcode id=3259 lang=python3
#
# [3259] Maximum Energy Boost From Two Drinks
#
# https://leetcode.com/problems/maximum-energy-boost-from-two-drinks/description/
#
# algorithms
# Medium (49.89%)
# Likes:    183
# Dislikes: 14
# Total Accepted:    36.6K
# Total Submissions: 73.3K
# Testcase Example:  "[1,3,1]\n[3,1,1]"
#
#
# You are given two integer arrays energyDrinkA and energyDrinkB of the
# same length n by a futuristic sports scientist. These arrays represent
# the energy boosts per hour provided by two different energy drinks, A
# and B, respectively.
#
# You want to maximize your total energy boost by drinking one energy
# drink per hour. However, if you want to switch from consuming one energy
# drink to the other, you need to wait for one hour to cleanse your system
# (meaning you won't get any energy boost in that hour).
#
# Return the maximum total energy boost you can gain in the next n hours.
#
# Note that you can start consuming either of the two energy drinks.
#
# Example 1:
#
# Input: energyDrinkA = [1,3,1], energyDrinkB = [3,1,1]
#
# Output: 5
#
# Explanation:
#
# To gain an energy boost of 5, drink only the energy drink A (or only B).
#
# Example 2:
#
# Input: energyDrinkA = [4,1,1], energyDrinkB = [1,1,3]
#
# Output: 7
#
# Explanation:
#
# To gain an energy boost of 7:
#
# Drink the energy drink A for the first hour.
#
# Switch to the energy drink B and we lose the energy boost of the second
# hour.
#
# Gain the energy boost of the drink B in the third hour.
#
# Constraints:
#
# n == energyDrinkA.length == energyDrinkB.length
#
# 3 <= n <= 10^5
#
# 1 <= energyDrinkA[i], energyDrinkB[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def maxEnergyBoost(self, energyDrinkA: List[int], energyDrinkB: List[int]) -> int:
        """
        Interview explanation:
        Drink A or B each hour; switching requires a wasted cleanse hour.
        DP on the last drink type.

        Algorithm:
        - dpA[i] / dpB[i]: max ending at hour i drinking A / B.
        - Continue same drink, or come from the other drink two hours earlier
          (cleanse in between).

        Complexity: O(n) time, O(1) space with rolling vars.
        """
        n = len(energyDrinkA)
        a_prev2 = b_prev2 = 0
        a_prev1 = energyDrinkA[0]
        b_prev1 = energyDrinkB[0]
        for i in range(1, n):
            a_cur = energyDrinkA[i] + max(a_prev1, b_prev2)
            b_cur = energyDrinkB[i] + max(b_prev1, a_prev2)
            a_prev2, b_prev2 = a_prev1, b_prev1
            a_prev1, b_prev1 = a_cur, b_cur
        return max(a_prev1, b_prev1)
# @lc code=end
