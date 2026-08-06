#
# @lc app=leetcode id=2036 lang=python3
#
# [2036] Maximum Alternating Subarray Sum
#
# https://leetcode.com/problems/maximum-alternating-subarray-sum/description/
#
# algorithms
# Medium (40.00%)
# Likes:    107
# Dislikes: 6
# Total Accepted:    4.5K
# Total Submissions: 11.2K
# Testcase Example:  "[3,-1,1,2]"
#
#
# A subarray of a 0-indexed integer array is a contiguous non-empty
# sequence of elements within an array.
#
# The alternating subarray sum of a subarray that ranges from index i to j
# (inclusive, 0 <= i <= j < nums.length) is nums[i] - nums[i+1] +
# nums[i+2] - ... +/- nums[j].
#
# Given a 0-indexed integer array nums, return the maximum alternating
# subarray sum of any subarray of nums.
#
# Example 1:
#
# Input: nums = [3,-1,1,2]
# Output: 5
# Explanation:
# The subarray [3,-1,1] has the largest alternating subarray sum.
# The alternating subarray sum is 3 - (-1) + 1 = 5.
#
# Example 2:
#
# Input: nums = [2,2,2,2,2]
# Output: 2
# Explanation:
# The subarrays [2], [2,2,2], and [2,2,2,2,2] have the largest alternating
# subarray sum.
# The alternating subarray sum of [2] is 2.
# The alternating subarray sum of [2,2,2] is 2 - 2 + 2 = 2.
# The alternating subarray sum of [2,2,2,2,2] is 2 - 2 + 2 - 2 + 2 = 2.
#
# Example 3:
#
# Input: nums = [1]
# Output: 1
# Explanation:
# There is only one non-empty subarray, which is [1].
# The alternating subarray sum is 1.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -10^5 <= nums[i] <= 10^5
#
# @lc code=start
from typing import List


class Solution:
    def maximumAlternatingSubarraySum(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Premium: max alternating sum of a contiguous subarray:
        a0 - a1 + a2 - a3 + ... Maximize over all subarrays.

        Algorithm:
        - DP: even = best ending here with even length pattern starting +;
          odd similarly. Or track best ending with last sign + / -.

        Complexity: O(n) time, O(1) space.
        """
        # end_pos: best alternating sum ending at i with last term added (+)
        # end_neg: best ending at i with last term subtracted (-)
        ans = nums[0]
        end_pos = nums[0]
        end_neg = float('-inf')
        for x in nums[1:]:
            new_pos = max(x, end_neg + x)  # start new or continue after a minus
            new_neg = end_pos - x          # must continue after a plus
            end_pos, end_neg = new_pos, new_neg
            ans = max(ans, end_pos, end_neg)
        return ans
# @lc code=end
