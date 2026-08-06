#
# @lc app=leetcode id=3976 lang=python3
#
# [3976] Maximum Subarray Sum After Multiplier
#
# https://leetcode.com/problems/maximum-subarray-sum-after-multiplier/description/
#
# algorithms
# Medium (26.23%)
# Likes:    104
# Dislikes: 8
# Total Accepted:    12.5K
# Total Submissions: 47.8K
# Testcase Example:  "[1,-2,3,4,-5]\n2"
#
#
# You are given an integer array nums and a positive integer k.
#
# You must choose exactly one subarray of nums and perform exactly one of
# the following operations:
#
# Multiply each number in the chosen subarray by k.
#
# Divide each number in the chosen subarray by k.
#
# When dividing a positive number by k, use the floor value of the
# division result.
#
# When dividing a negative number by k, use the ceiling value of the
# division result.
#
# Return the maximum possible sum of a non-empty subarray in the resulting
# array.
#
# Note that the subarray chosen for the operation and the subarray chosen
# for the sum may be different.
#
# Example 1:
#
# Input: nums = [1,-2,3,4,-5], k = 2
#
# Output: 14
#
# Explanation:
#
# Multiply each number in the subarray [3, 4] by 2.
#
# This results in nums = [1, -2, 6, 8, -5].
#
# The subarray with the largest sum is [6, 8], so the output is 6 + 8 =
# 14.
#
# Example 2:
#
# Input: nums = [-5,-4,-3], k = 2
#
# Output: -1
#
# Explanation:
#
# Divide each number in the subarray [-3] by 2.
#
# This results in nums = [-5, -4, -1].
#
# The subarray with the largest sum is [-1], so the output is -1.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -10^5 <= nums[i] <= 10^5
#
# 1 <= k <= 10^5
#

# @lc code=start

from math import inf
from typing import List


class Solution:
    def maxSubarraySum(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Kadane with four endings: no op yet, currently multiplying, currently
        dividing (trunc toward 0), and op already finished in the subarray.

        Algorithm:
        - f0 = continue/restart with raw x.
        - f1 = start/continue multiply with x*k.
        - f2 = start/continue divide with int(x/k).
        - f3 = after an op, append raw x.
        - Answer is the max over all states and positions (op can sit outside the
          summed region, so the no-op Kadane state is admissible for n >= 2).

        Complexity: O(n) time, O(1) extra space with rolling states.
        """
        n = len(nums)
        f = [[-inf] * 4 for _ in range(n + 1)]
        f[0][0] = 0
        ans = -inf
        for i, x in enumerate(nums, 1):
            f[i][0] = max(f[i - 1][0], 0) + x
            f[i][1] = max(f[i - 1][0], f[i - 1][1], 0) + x * k
            f[i][2] = max(f[i - 1][0], f[i - 1][2], 0) + int(x / k)
            f[i][3] = max(f[i - 1][1], f[i - 1][2], f[i - 1][3]) + x
            ans = max(ans, max(f[i]))
        return ans
# @lc code=end
