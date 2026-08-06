#
# @lc app=leetcode id=1413 lang=python3
#
# [1413] Minimum Value to Get Positive Step by Step Sum
#
# https://leetcode.com/problems/minimum-value-to-get-positive-step-by-step-sum/description/
#
# algorithms
# Easy (64.81%)
# Likes:    1698
# Dislikes: 390
# Total Accepted:    239K
# Total Submissions: 369K
# Testcase Example:  "[-3,2,-3,4,2]"
#
# Given an array of integers nums, you start with an initial positive value
# startValue.
#
# In each iteration, you calculate the step by step sum of startValue plus
# elements in nums (from left to right).
#
# Return the minimum positive value of startValue such that the step by step
# sum is never less than 1.
#
# Example 1:
#
# Input: nums = [-3,2,-3,4,2]
# Output: 5
# Explanation: If you choose startValue = 4, in the third iteration your step
# by step sum is less than 1.
# step by step sum
# startValue = 4 | startValue = 5 | nums
# (4 -3 ) = 1 | (5 -3 ) = 2 | -3
# (1 +2 ) = 3 | (2 +2 ) = 4 | 2
# (3 -3 ) = 0 | (4 -3 ) = 1 | -3
# (0 +4 ) = 4 | (1 +4 ) = 5 | 4
# (4 +2 ) = 6 | (5 +2 ) = 7 | 2
#
# Example 2:
#
# Input: nums = [1,2]
# Output: 1
# Explanation: Minimum start value should be positive.
#
# Example 3:
#
# Input: nums = [1,-2,-3]
# Output: 5
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# -100 <= nums[i] <= 100
#

# @lc code=start
from typing import List


class Solution:
    def minStartValue(self, nums: List[int]) -> int:
        """
        Interview explanation:
        startValue + prefix must stay >=1 always. Equivalently startValue >=
        1 - min_prefix. If all prefixes non-negative, answer is 1.

        Algorithm:
        (prefix min)
        - Track running sum and its minimum; return max(1, 1 - min_pref)

        Complexity: O(n) time, O(1) space.
        """
        pref = mn = 0
        for x in nums:
            pref += x
            mn = min(mn, pref)
        return max(1, 1 - mn)

    def minStartValue_binary(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: binary search the minimal startValue in [1, 1+sum(abs)].

        Algorithm:
        - Check(mid): simulate mid+prefix always >=1; binary search lowest mid.

        Complexity: O(n log S) time, O(1) space.
        """
        lo, hi = 1, 1 + sum(abs(x) for x in nums)

        def ok(start: int) -> bool:
            cur = start
            for x in nums:
                cur += x
                if cur < 1:
                    return False
            return True

        while lo < hi:
            mid = (lo + hi) // 2
            if ok(mid):
                hi = mid
            else:
                lo = mid + 1
        return lo
# @lc code=end
