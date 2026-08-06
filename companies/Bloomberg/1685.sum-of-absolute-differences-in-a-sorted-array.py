#
# @lc app=leetcode id=1685 lang=python3
#
# [1685] Sum of Absolute Differences in a Sorted Array
#
# https://leetcode.com/problems/sum-of-absolute-differences-in-a-sorted-array/description/
#
# algorithms
# Medium (68.5%)
# Likes:    2246
# Dislikes: 85
# Total Accepted:    141K
# Total Submissions: 206K
# Testcase Example:  "[2,3,5]"
#
# You are given an integer array nums sorted in non-decreasing order.
#
# Build and return an integer array result with the same length as nums such
# that result[i] is equal to the summation of absolute differences between
# nums[i] and all the other elements in the array.
#
# In other words, result[i] is equal to sum(|nums[i]-nums[j]|) where 0 <= j <
# nums.length and j != i (0-indexed).
#
# Example 1:
#
# Input: nums = [2,3,5]
# Output: [4,3,5]
# Explanation: Assuming the arrays are 0-indexed, then
# result[0] = |2-2| + |2-3| + |2-5| = 0 + 1 + 3 = 4,
# result[1] = |3-2| + |3-3| + |3-5| = 1 + 0 + 2 = 3,
# result[2] = |5-2| + |5-3| + |5-5| = 3 + 2 + 0 = 5.
#
# Example 2:
#
# Input: nums = [1,4,6,8,10]
# Output: [24,15,13,15,21]
#
# Constraints:
#
# 2 <= nums.length <= 10^5
#
# 1 <= nums[i] <= nums[i + 1] <= 10^4
#

# @lc code=start
from typing import List


class Solution:
    def getSumAbsoluteDifferences(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Sorted array: result[i] = sum |nums[i]-nums[j]|. Split into left
        (nums[i]*i - left_sum) + (right_sum - nums[i]*(n-i-1)).

        Algorithm (prefix):
        - total=sum; left=0; for i: right=total-left-nums[i];
          ans[i]=nums[i]*i-left + right-nums[i]*(n-i-1); left+=nums[i]

        Complexity: O(n) time, O(n) space for answer.
        """
        n = len(nums)
        total = sum(nums)
        left = 0
        ans = [0] * n
        for i, v in enumerate(nums):
            right = total - left - v
            ans[i] = v * i - left + right - v * (n - i - 1)
            left += v
        return ans
# @lc code=end
