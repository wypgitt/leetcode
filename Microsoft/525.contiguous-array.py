#
# @lc app=leetcode id=525 lang=python3
#
# [525] Contiguous Array
#
# https://leetcode.com/problems/contiguous-array/description/
#
# algorithms
# Medium (51.98%)
# Likes:    8990
# Dislikes: 452
# Total Accepted:    718K
# Total Submissions: 1.4M
# Testcase Example:  "[0,1]"
#
# Given a binary array nums, return the maximum length of a contiguous subarray
# with an equal number of 0 and 1.
#
# Example 1:
#
# Input: nums = [0,1]
# Output: 2
# Explanation: [0, 1] is the longest contiguous subarray with an equal number
# of 0 and 1.
#
# Example 2:
#
# Input: nums = [0,1,0]
# Output: 2
# Explanation: [0, 1] (or [1, 0]) is a longest contiguous subarray with equal
# number of 0 and 1.
#
# Example 3:
#
# Input: nums = [0,1,1,1,1,1,0,0,0]
# Output: 6
# Explanation: [1,1,1,0,0,0] is the longest contiguous subarray with equal
# number of 0 and 1.
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
    def findMaxLength(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Treat 0 as -1. Equal 0s and 1s iff prefix sum returns to a previous
        value; longest distance between same prefix is the answer.

        Algorithm:
        - Map prefix_sum -> first index; seed {0: -1}.
        - Update ans = max(ans, i - first[prefix]) when prefix repeats.

        Complexity: O(n) time, O(n) space.
        """
        first = {0: -1}
        prefix = 0
        ans = 0
        for i, x in enumerate(nums):
            prefix += 1 if x == 1 else -1
            if prefix in first:
                ans = max(ans, i - first[prefix])
            else:
                first[prefix] = i
        return ans
# @lc code=end
