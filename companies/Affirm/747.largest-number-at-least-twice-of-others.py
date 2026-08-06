#
# @lc app=leetcode id=747 lang=python3
#
# [747] Largest Number At Least Twice of Others
#
# https://leetcode.com/problems/largest-number-at-least-twice-of-others/description/
#
# algorithms
# Easy (52.94%)
# Likes:    1396
# Dislikes: 962
# Total Accepted:    355K
# Total Submissions: 670K
# Testcase Example:  "[3,6,1,0]"
#
# You are given an integer array nums where the largest integer is unique.
#
# Determine whether the largest element in the array is at least twice as much
# as every other number in the array. If it is, return the index of the largest
# element, or return -1 otherwise.
#
# Example 1:
#
# Input: nums = [3,6,1,0]
# Output: 1
# Explanation: 6 is the largest integer.
# For every other number in the array x, 6 is at least twice as big as x.
# The index of value 6 is 1, so we return 1.
#
# Example 2:
#
# Input: nums = [1,2,3,4]
# Output: -1
# Explanation: 4 is less than twice the value of 3, so we return -1.
#
# Constraints:
#
# 2 <= nums.length <= 50
#
# 0 <= nums[i] <= 100
#
# The largest element in nums is unique.
#


# @lc code=start
from typing import List


class Solution:
    def dominantIndex(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Find the largest element's index; it is dominant iff it is >= twice
        every other element (equivalently >= twice the second largest).

        Algorithm:
        - Track max1, max2 and index of max1 in one pass
        - Return idx if max1 >= 2 * max2 else -1

        Complexity: O(n) time, O(1) space.
        """
        max1 = max2 = -1
        idx = -1
        for i, x in enumerate(nums):
            if x > max1:
                max2, max1, idx = max1, x, i
            elif x > max2:
                max2 = x
        return idx if max1 >= 2 * max2 else -1
# @lc code=end

