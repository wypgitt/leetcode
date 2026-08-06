#
# @lc app=leetcode id=1749 lang=python3
#
# [1749] Maximum Absolute Sum of Any Subarray
#
# https://leetcode.com/problems/maximum-absolute-sum-of-any-subarray/description/
#
# algorithms
# Medium (70.78%)
# Likes:    2048
# Dislikes: 52
# Total Accepted:    207K
# Total Submissions: 293K
# Testcase Example:  "[1,-3,2,3,-4]"
#
# You are given an integer array nums. The absolute sum of a subarray [nums_l,
# nums_l+1, ..., nums_r-1, nums_r] is abs(nums_l + nums_l+1 + ... + nums_r-1 +
# nums_r).
#
# Return the maximum absolute sum of any (possibly empty) subarray of nums.
#
# Note that abs(x) is defined as follows:
#
# If x is a negative integer, then abs(x) = -x.
#
# If x is a non-negative integer, then abs(x) = x.
#
# Example 1:
#
# Input: nums = [1,-3,2,3,-4]
# Output: 5
# Explanation: The subarray [2,3] has absolute sum = abs(2+3) = abs(5) = 5.
#
# Example 2:
#
# Input: nums = [2,-5,1,-4,3,-2]
# Output: 8
# Explanation: The subarray [-5,1,-4] has absolute sum = abs(-5+1-4) = abs(-8)
# = 8.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -10^4 <= nums[i] <= 10^4
#

# @lc code=start
from typing import List


class Solution:
    def maxAbsoluteSum(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Max |subarray sum| equals max of (max subarray sum, -min subarray sum).
        Run Kadane for both max and min.

        Algorithm:
        - Track max_ending/min_ending and globals; return max(max_sum, -min_sum).

        Complexity: O(n) time, O(1) space.
        """
        max_end = min_end = 0
        max_sum = min_sum = 0
        for x in nums:
            max_end = max(x, max_end + x)
            min_end = min(x, min_end + x)
            max_sum = max(max_sum, max_end)
            min_sum = min(min_sum, min_end)
        return max(max_sum, -min_sum)

    def maxAbsoluteSum_prefix(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: max |pref[j]-pref[i]| over prefixes is max(pref)-min(pref).

        Algorithm:
        - Build prefix sums including 0; return max - min.

        Complexity: O(n) time, O(n) space.
        """
        pref = [0]
        for x in nums:
            pref.append(pref[-1] + x)
        return max(pref) - min(pref)
# @lc code=end
