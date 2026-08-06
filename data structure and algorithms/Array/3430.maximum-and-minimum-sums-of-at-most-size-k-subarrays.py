#
# @lc app=leetcode id=3430 lang=python3
#
# [3430] Maximum and Minimum Sums of at Most Size K Subarrays
#
# https://leetcode.com/problems/maximum-and-minimum-sums-of-at-most-size-k-subarrays/description/
#
# algorithms
# Hard (26.40%)
# Likes:    91
# Dislikes: 9
# Total Accepted:    4.9K
# Total Submissions: 18.6K
# Testcase Example:  "[1,2,3]\n2"
#
#
# You are given an integer array nums and a positive integer k. Return the
# sum of the maximum and minimum elements of all subarrays with at most k
# elements.
#
# Example 1:
#
# Input: nums = [1,2,3], k = 2
#
# Output: 20
#
# Explanation:
#
# The subarrays of nums with at most 2 elements are:
#
#                         Subarray
#                         Minimum
#                         Maximum
#                         Sum
#
#                         [1]
#                         1
#                         1
#                         2
#
#                         [2]
#                         2
#                         2
#                         4
#
#                         [3]
#                         3
#                         3
#                         6
#
#                         [1, 2]
#                         1
#                         2
#                         3
#
#                         [2, 3]
#                         2
#                         3
#                         5
#
#                         Final Total
#
#                         20
#
# The output would be 20.
#
# Example 2:
#
# Input: nums = [1,-3,1], k = 2
#
# Output: -6
#
# Explanation:
#
# The subarrays of nums with at most 2 elements are:
#
#                         Subarray
#                         Minimum
#                         Maximum
#                         Sum
#
#                         [1]
#                         1
#                         1
#                         2
#
#                         [-3]
#                         -3
#                         -3
#                         -6
#
#                         [1]
#                         1
#                         1
#                         2
#
#                         [1, -3]
#                         -3
#                         1
#                         -2
#
#                         [-3, 1]
#                         -3
#                         1
#                         -2
#
#                         Final Total
#
#                         -6
#
# The output would be -6.
#
# Constraints:
#
# 1 <= nums.length <= 80000
#
# 1 <= k <= nums.length
#
# -10^6 <= nums[i] <= 10^6
#

# @lc code=start
import operator
from typing import List


class Solution:
    def minMaxSubarraySum(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Sum of mins over subarrays of length <= k plus sum of maxes. For each
        index, count how many length-<=k subarrays have it as strict extremum via
        previous/next greater (or lesser) neighbors.

        Algorithm:
        - Monotonic stack: prev/next greater and prev/next lesser.
        - For nums[i] as extremum: l = min(i-prev, k), r = min(next-i, k);
          count = l*r - extra*(extra+1)/2 where extra = max(0, l+r-1-k).
        - Add nums[i]*count for both max and min roles.

        Complexity: O(n) time, O(n) space.
        """
        prev_gt, next_gt = self._get_prev_next(nums, operator.lt)
        prev_lt, next_lt = self._get_prev_next(nums, operator.gt)
        return (
            self._subarray_sum(nums, prev_gt, next_gt, k)
            + self._subarray_sum(nums, prev_lt, next_lt, k)
        )

    def _subarray_sum(
        self, nums: List[int], prev: List[int], nxt: List[int], k: int
    ) -> int:
        res = 0
        for i, num in enumerate(nums):
            l = min(i - prev[i], k)
            r = min(nxt[i] - i, k)
            extra = max(0, l + r - 1 - k)
            res += num * (l * r - extra * (extra + 1) // 2)
        return res

    def _get_prev_next(self, nums: List[int], op) -> tuple:
        n = len(nums)
        prev = [-1] * n
        nxt = [n] * n
        stack: List[int] = []
        for i, num in enumerate(nums):
            while stack and op(nums[stack[-1]], num):
                nxt[stack.pop()] = i
            if stack:
                prev[i] = stack[-1]
            stack.append(i)
        return prev, nxt
# @lc code=end
