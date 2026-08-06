#
# @lc app=leetcode id=1018 lang=python3
#
# [1018] Binary Prefix Divisible By 5
#
# https://leetcode.com/problems/binary-prefix-divisible-by-5/description/
#
# algorithms
# Easy (53.72%)
# Likes:    1118
# Dislikes: 231
# Total Accepted:    188K
# Total Submissions: 350K
# Testcase Example:  "[0,1,1]"
#
# You are given a binary array nums (0-indexed).
#
# We define x_i as the number whose binary representation is the subarray
# nums[0..i] (from most-significant-bit to least-significant-bit).
#
# For example, if nums = [1,0,1], then x_0 = 1, x_1 = 2, and x_2 = 5.
#
# Return an array of booleans answer where answer[i] is true if x_i is
# divisible by 5.
#
# Example 1:
#
# Input: nums = [0,1,1]
# Output: [true,false,false]
# Explanation: The input numbers in binary are 0, 01, 011; which are 0, 1, and
# 3 in base-10.
# Only the first number is divisible by 5, so answer[0] is true.
#
# Example 2:
#
# Input: nums = [1,1,1]
# Output: [false,false,false]
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# nums[i] is either 0 or 1.
#

# @lc code=start
from typing import List


class Solution:
    def prefixesDivBy5(self, nums: List[int]) -> List[bool]:
        """
        Interview explanation:
        Running value is formed as val = val*2 + bit. Only need val mod 5, so
        keep remainder: rem = (rem*2 + bit) % 5; append rem==0.

        Algorithm:
        - rem=0; for each bit: rem=(rem*2+bit)%5; ans.append(rem==0)

        Complexity: O(n) time, O(1) extra space.
        """
        ans = []
        rem = 0
        for bit in nums:
            rem = (rem * 2 + bit) % 5
            ans.append(rem == 0)
        return ans
# @lc code=end
