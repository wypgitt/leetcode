#
# @lc app=leetcode id=485 lang=python3
#
# [485] Max Consecutive Ones
#
# https://leetcode.com/problems/max-consecutive-ones/description/
#
# algorithms
# Easy (65.82%)
# Likes:    7021
# Dislikes: 502
# Total Accepted:    2.5M
# Total Submissions: 3.8M
# Testcase Example:  "[1,1,0,1,1,1]"
#
# Given a binary array nums, return the maximum number of consecutive 1's in
# the array.
#
# Example 1:
#
# Input: nums = [1,1,0,1,1,1]
# Output: 3
# Explanation: The first two digits or the last three digits are consecutive
# 1s. The maximum number of consecutive 1s is 3.
#
# Example 2:
#
# Input: nums = [1,0,1,1,0,1]
# Output: 2
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
    def findMaxConsecutiveOnes(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Single scan: count streak of 1s; reset on 0; track maximum streak.

        Algorithm:
        - cur = ans = 0; for x in nums: cur = cur+1 if x else 0; ans = max(ans, cur).

        Complexity: O(n) time, O(1) space.
        """
        ans = cur = 0
        for x in nums:
            if x == 1:
                cur += 1
                ans = max(ans, cur)
            else:
                cur = 0
        return ans
# @lc code=end
