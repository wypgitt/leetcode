#
# @lc app=leetcode id=2553 lang=python3
#
# [2553] Separate the Digits in an Array
#
# https://leetcode.com/problems/separate-the-digits-in-an-array/description/
#
# algorithms
# Easy (85.77%)
# Likes:    730
# Dislikes: 18
# Total Accepted:    237.2K
# Total Submissions: 276.6K
# Testcase Example:  "[13,25,83,77]"
#
# Given an array of positive integers nums, return an array answer that consists
# of the digits of each integer in nums after separating them in the same order
# they appear in nums.
#
# To separate the digits of an integer is to get all the digits it has in the
# same order.
#
#
# For example, for the integer 10921, the separation of its digits is
# [1,0,9,2,1].
#
#
#
# Example 1:
#
# Input: nums = [13,25,83,77]
# Output: [1,3,2,5,8,3,7,7]
# Explanation:
# - The separation of 13 is [1,3].
# - The separation of 25 is [2,5].
# - The separation of 83 is [8,3].
# - The separation of 77 is [7,7].
# answer = [1,3,2,5,8,3,7,7]. Note that answer contains the separations in the
# same order.
#
# Example 2:
#
# Input: nums = [7,1,3,9]
# Output: [7,1,3,9]
# Explanation: The separation of each integer in nums is itself.
# answer = [7,1,3,9].
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 1000
#
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def separateDigits(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Expand each integer into its decimal digits in order.

        Algorithm:
        - For each num, convert to string (or peel digits) and append digits.

        Complexity: O(total digits) time and space.
        """
        ans = []
        for x in nums:
            ans.extend(int(d) for d in str(x))
        return ans
# @lc code=end
