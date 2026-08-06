#
# @lc app=leetcode id=3173 lang=python3
#
# [3173] Bitwise OR of Adjacent Elements
#
# https://leetcode.com/problems/bitwise-or-of-adjacent-elements/description/
#
# algorithms
# Easy (94.72%)
# Likes:    25
# Dislikes: 2
# Total Accepted:    6.9K
# Total Submissions: 7.3K
# Testcase Example:  "[1,3,7,15]"
#
#
# Given an array nums of length n, return an array answer of length n - 1
# such that answer[i] = nums[i] | nums[i + 1] where | is the bitwise OR
# operation.
#
# Example 1:
#
# Input: nums = [1,3,7,15]
#
# Output: [3,7,15]
#
# Example 2:
#
# Input: nums = [8,4,2]
#
# Output: [12,6]
#
# Example 3:
#
# Input: nums = [5,4,9,11]
#
# Output: [5,13,11]
#
# Constraints:
#
# 2 <= nums.length <= 100
#
# 0 <= nums[i] <= 100
#

# @lc code=start
from typing import List


class Solution:
    def orArray(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Build answer[i] = nums[i] | nums[i+1] for each adjacent pair.

        Algorithm:
        - One pass zip of nums[:-1] with nums[1:].

        Complexity: O(n) time, O(n) space for the output.
        """
        return [nums[i] | nums[i + 1] for i in range(len(nums) - 1)]

    def orArray_loop(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate: explicit loop appending each adjacent OR.

        Algorithm:
        - For i in 0..n-2 append nums[i] | nums[i+1].

        Complexity: O(n) time, O(n) space.
        """
        ans: list[int] = []
        for i in range(len(nums) - 1):
            ans.append(nums[i] | nums[i + 1])
        return ans
# @lc code=end
