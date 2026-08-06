#
# @lc app=leetcode id=976 lang=python3
#
# [976] Largest Perimeter Triangle
#
# https://leetcode.com/problems/largest-perimeter-triangle/description/
#
# algorithms
# Easy (62.39%)
# Likes:    3419
# Dislikes: 444
# Total Accepted:    439K
# Total Submissions: 704K
# Testcase Example:  "[2,1,2]"
#
# Given an integer array nums, return the largest perimeter of a triangle with
# a non-zero area, formed from three of these lengths. If it is impossible to
# form any triangle of a non-zero area, return 0.
#
# Example 1:
#
# Input: nums = [2,1,2]
# Output: 5
# Explanation: You can form a triangle with three side lengths: 1, 2, and 2.
#
# Example 2:
#
# Input: nums = [1,2,1,10]
# Output: 0
#
# Explanation:
# You cannot use the side lengths 1, 1, and 2 to form a triangle.
# You cannot use the side lengths 1, 1, and 10 to form a triangle.
# You cannot use the side lengths 1, 2, and 10 to form a triangle.
# As we cannot use any three side lengths to form a triangle of non-zero area,
# we return 0.
#
# Constraints:
#
# 3 <= nums.length <= 10^4
#
# 1 <= nums[i] <= 10^6
#

# @lc code=start
from typing import List


class Solution:
    def largestPerimeter(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Largest perimeter valid triangle: sort descending and take the first
        triple (a,b,c) with a < b+c (strict triangle inequality). Greedy works
        because larger sides maximize perimeter and any later smaller triple
        cannot beat an earlier valid one.

        Algorithm:
        - Sort nums descending.
        - For i in 0..n-3: if nums[i] < nums[i+1]+nums[i+2] return sum.
        - Else return 0.

        Complexity: O(n log n) time, O(1) or O(n) space (sort).
        """
        nums.sort(reverse=True)
        for i in range(len(nums) - 2):
            if nums[i] < nums[i + 1] + nums[i + 2]:
                return nums[i] + nums[i + 1] + nums[i + 2]
        return 0
# @lc code=end
