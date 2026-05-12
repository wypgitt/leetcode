#
# @lc app=leetcode id=1276 lang=python3
#
# [1276] Number of Burgers with No Waste of Ingredients
#
# https://leetcode.com/problems/number-of-burgers-with-no-waste-of-ingredients/description/
#
# algorithms
# Medium (50.98%)
# Likes:    347
# Dislikes: 239
# Total Accepted:    33.2K
# Total Submissions: 65.1K
# Testcase Example:  '16\n7'
#
# Given two integers tomatoSlices and cheeseSlices. The ingredients of
# different burgers are as follows:
# 
# 
# Jumbo Burger: 4 tomato slices and 1 cheese slice.
# Small Burger: 2 Tomato slices and 1 cheese slice.
# 
# 
# Return [total_jumbo, total_small] so that the number of remaining
# tomatoSlices equal to 0 and the number of remaining cheeseSlices equal to 0.
# If it is not possible to make the remaining tomatoSlices and cheeseSlices
# equal to 0 return [].
# 
# 
# Example 1:
# 
# 
# Input: tomatoSlices = 16, cheeseSlices = 7
# Output: [1,6]
# Explantion: To make one jumbo burger and 6 small burgers we need 4*1 + 2*6 =
# 16 tomato and 1 + 6 = 7 cheese.
# There will be no remaining ingredients.
# 
# 
# Example 2:
# 
# 
# Input: tomatoSlices = 17, cheeseSlices = 4
# Output: []
# Explantion: There will be no way to use all ingredients to make small and
# jumbo burgers.
# 
# 
# Example 3:
# 
# 
# Input: tomatoSlices = 4, cheeseSlices = 17
# Output: []
# Explantion: Making 1 jumbo burger there will be 16 cheese remaining and
# making 2 small burgers there will be 15 cheese remaining.
# 
# 
# 
# Constraints:
# 
# 
# 0 <= tomatoSlices, cheeseSlices <= 10^7
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def numOfBurgers(self, tomatoSlices: int, cheeseSlices: int) -> List[int]:
        extra_tomatoes = tomatoSlices - 2 * cheeseSlices

        if extra_tomatoes < 0 or extra_tomatoes % 2 != 0:
            return []

        jumbo = extra_tomatoes // 2
        small = cheeseSlices - jumbo

        if small < 0:
            return []

        return [jumbo, small]
# @lc code=end

# Explanation
# -----------
# Let jumbo = x and small = y. The equations are:
# x + y = cheeseSlices and 4x + 2y = tomatoSlices. Subtracting
# 2 * cheeseSlices from tomatoSlices leaves 2x, so
# x = (tomatoSlices - 2 * cheeseSlices) / 2.
#
# After computing jumbo, small is cheeseSlices - jumbo. Both must be
# nonnegative integers.
#
# Edge cases: odd tomato difference cannot split into integer jumbo burgers;
# too few tomato slices; computed jumbo greater than cheese slices.
#
# Time complexity: O(1).
# Space complexity: O(1).
