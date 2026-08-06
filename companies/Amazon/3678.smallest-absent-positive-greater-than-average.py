#
# @lc app=leetcode id=3678 lang=python3
#
# [3678] Smallest Absent Positive Greater Than Average
#
# https://leetcode.com/problems/smallest-absent-positive-greater-than-average/description/
#
# algorithms
# Easy (34.51%)
# Likes:    67
# Dislikes: 6
# Total Accepted:    39.3K
# Total Submissions: 113.7K
# Testcase Example:  "[3,5]"
#
#
# You are given an integer array nums.
#
# Return the smallest absent positive integer in nums such that it is
# strictly greater than the average of all elements in nums.
#
# The average of an array is defined as the sum of all its elements
# divided by the number of elements.
#
# Example 1:
#
# Input: nums = [3,5]
#
# Output: 6
#
# Explanation:
#
# The average of nums is (3 + 5) / 2 = 8 / 2 = 4.
#
# The smallest absent positive integer greater than 4 is 6.
#
# Example 2:
#
# Input: nums = [-1,1,2]
#
# Output: 3
#
# Explanation:
#
# ​​​​​​​The average of nums is (-1 + 1 + 2) / 3 = 2 / 3 = 0.667.
#
# The smallest absent positive integer greater than 0.667 is 3.
#
# Example 3:
#
# Input: nums = [4,-1]
#
# Output: 2
#
# Explanation:
#
# The average of nums is (4 + (-1)) / 2 = 3 / 2 = 1.50.
#
# The smallest absent positive integer greater than 1.50 is 2.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# -100 <= nums[i] <= 100​​​​​​​
#

# @lc code=start
import math
from typing import List


class Solution:
    def smallestAbsent(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Find the least positive integer missing from nums that is strictly
        greater than the average.

        Algorithm:
        - avg = sum/n; start candidate at max(1, floor(avg)+1).
        - Increment while the candidate is present in a set of nums.

        Complexity: O(n + U) time with tiny U under constraints, O(n) space.
        """
        avg = sum(nums) / len(nums)
        present = set(nums)
        x = max(1, math.floor(avg) + 1)
        while x in present:
            x += 1
        return x
# @lc code=end
