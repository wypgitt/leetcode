#
# @lc app=leetcode id=3024 lang=python3
#
# [3024] Type of Triangle
#
# https://leetcode.com/problems/type-of-triangle/description/
#
# algorithms
# Easy (44.01%)
# Likes:    476
# Dislikes: 69
# Total Accepted:    226K
# Total Submissions: 513.6K
# Testcase Example:  "[3,3,3]"
#
#
# You are given a 0-indexed integer array nums of size 3 which can form
# the sides of a triangle.
#
# A triangle is called equilateral if it has all sides of equal length.
#
# A triangle is called isosceles if it has exactly two sides of equal
# length.
#
# A triangle is called scalene if all its sides are of different lengths.
#
# Return a string representing the type of triangle that can be formed or
# "none" if it cannot form a triangle.
#
# Example 1:
#
# Input: nums = [3,3,3]
# Output: "equilateral"
# Explanation: Since all the sides are of equal length, therefore, it will
# form an equilateral triangle.
#
# Example 2:
#
# Input: nums = [3,4,5]
# Output: "scalene"
# Explanation:
# nums[0] + nums[1] = 3 + 4 = 7, which is greater than nums[2] = 5.
# nums[0] + nums[2] = 3 + 5 = 8, which is greater than nums[1] = 4.
# nums[1] + nums[2] = 4 + 5 = 9, which is greater than nums[0] = 3.
# Since the sum of the two sides is greater than the third side for all
# three cases, therefore, it can form a triangle.
# As all the sides are of different lengths, it will form a scalene
# triangle.
#
# Constraints:
#
# nums.length == 3
#
# 1 <= nums[i] <= 100
#

# @lc code=start

from typing import List


class Solution:
    def triangleType(self, nums: List[int]) -> str:
        """
        Interview explanation:
        Classify a 3-side array as equilateral / isosceles / scalene, or none
        if it cannot form a triangle.

        Algorithm:
        - Sort a<=b<=c. Invalid if a+b<=c.
        - All equal -> equilateral; exactly two equal -> isosceles; else scalene.

        Complexity: O(1) time, O(1) space.
        """
        a, b, c = sorted(nums)
        if a + b <= c:
            return "none"
        if a == c:
            return "equilateral"
        if a == b or b == c:
            return "isosceles"
        return "scalene"
# @lc code=end
