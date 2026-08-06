#
# @lc app=leetcode id=3494 lang=python3
#
# [3494] Find the Minimum Amount of Time to Brew Potions
#
# https://leetcode.com/problems/find-the-minimum-amount-of-time-to-brew-potions/description/
#
# algorithms
# Medium (62.68%)
# Likes:    512
# Dislikes: 363
# Total Accepted:    87.7K
# Total Submissions: 139.9K
# Testcase Example:  "[1,5,2,4]\n[5,1,4,2]"
#
#
# You are given two integer arrays, skill and mana, of length n and m,
# respectively.
#
# In a laboratory, n wizards must brew m potions in order. Each potion has
# a mana capacity mana[j] and must pass through all the wizards
# sequentially to be brewed properly. The time taken by the i^th wizard on
# the j^th potion is time_ij = skill[i] * mana[j].
#
# Since the brewing process is delicate, a potion must be passed to the
# next wizard immediately after the current wizard completes their work.
# This means the timing must be synchronized so that each wizard begins
# working on a potion exactly when it arrives. ​
#
# Return the minimum amount of time required for the potions to be brewed
# properly.
#
# Example 1:
#
# Input: skill = [1,5,2,4], mana = [5,1,4,2]
#
# Output: 110
#
# Explanation:
#
#                         Potion Number
#                         Start time
#                         Wizard 0 done by
#                         Wizard 1 done by
#                         Wizard 2 done by
#                         Wizard 3 done by
#
#                         0
#                         0
#                         5
#                         30
#                         40
#                         60
#
#                         1
#                         52
#                         53
#                         58
#                         60
#                         64
#
#                         2
#                         54
#                         58
#                         78
#                         86
#                         102
#
#                         3
#                         86
#                         88
#                         98
#                         102
#                         110
#
# As an example for why wizard 0 cannot start working on the 1^st potion
# before time t = 52, consider the case where the wizards started
# preparing the 1^st potion at time t = 50. At time t = 58, wizard 2 is
# done with the 1^st potion, but wizard 3 will still be working on the
# 0^th potion till time t = 60.
#
# Example 2:
#
# Input: skill = [1,1,1], mana = [1,1,1]
#
# Output: 5
#
# Explanation:
#
# Preparation of the 0^th potion begins at time t = 0, and is completed by
# time t = 3.
#
# Preparation of the 1^st potion begins at time t = 1, and is completed by
# time t = 4.
#
# Preparation of the 2^nd potion begins at time t = 2, and is completed by
# time t = 5.
#
# Example 3:
#
# Input: skill = [1,2,3,4], mana = [1,2]
#
# Output: 21
#
# Constraints:
#
# n == skill.length
#
# m == mana.length
#
# 1 <= n, m <= 5000
#
# 1 <= mana[i], skill[i] <= 5000
#

# @lc code=start
from typing import List


class Solution:
    def minTime(self, skill: List[int], mana: List[int]) -> int:
        """
        Interview explanation:
        Potions brew in order through wizards 0..n-1 with no waiting between
        consecutive wizards on the same potion (pipeline sync). Minimize finish
        time of the last potion on the last wizard.

        Algorithm:
        - Maintain finish[i] = time wizard i finished the previous potion.
        - For each potion: forward pass for earliest finish times, then
          backward pass to sync start times so handoffs are immediate.

        Complexity: O(n * m) time, O(n) space.
        """
        n = len(skill)
        done = [0] * n
        for x in mana:
            done[0] += skill[0] * x
            for i in range(1, n):
                done[i] = max(done[i], done[i - 1]) + skill[i] * x
            for i in range(n - 2, -1, -1):
                done[i] = done[i + 1] - skill[i + 1] * x
        return done[-1]
# @lc code=end
