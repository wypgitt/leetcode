#
# @lc app=leetcode id=3196 lang=python3
#
# [3196] Maximize Total Cost of Alternating Subarrays
#
# https://leetcode.com/problems/maximize-total-cost-of-alternating-subarrays/description/
#
# algorithms
# Medium (29.96%)
# Likes:    199
# Dislikes: 29
# Total Accepted:    26.4K
# Total Submissions: 88K
# Testcase Example:  "[1,-2,3,4]"
#
#
# You are given an integer array nums with length n.
#
# The cost of a subarray nums[l..r], where 0 <= l <= r < n, is defined as:
#
# cost(l, r) = nums[l] - nums[l + 1] + ... + nums[r] * (−1)^r − l
#
# Your task is to split nums into subarrays such that the total cost of
# the subarrays is maximized, ensuring each element belongs to exactly one
# subarray.
#
# Formally, if nums is split into k subarrays, where k > 1, at indices
# i_1, i_2, ..., i_k − 1, where 0 <= i_1 < i_2 < ... < i_k - 1 < n - 1,
# then the total cost will be:
#
# cost(0, i_1) + cost(i_1 + 1, i_2) + ... + cost(i_k − 1 + 1, n − 1)
#
# Return an integer denoting the maximum total cost of the subarrays after
# splitting the array optimally.
#
# Note: If nums is not split into subarrays, i.e. k = 1, the total cost is
# simply cost(0, n - 1).
#
# Example 1:
#
# Input: nums = [1,-2,3,4]
#
# Output: 10
#
# Explanation:
#
# One way to maximize the total cost is by splitting [1, -2, 3, 4] into
# subarrays [1, -2, 3] and [4]. The total cost will be (1 + 2 + 3) + 4 =
# 10.
#
# Example 2:
#
# Input: nums = [1,-1,1,-1]
#
# Output: 4
#
# Explanation:
#
# One way to maximize the total cost is by splitting [1, -1, 1, -1] into
# subarrays [1, -1] and [1, -1]. The total cost will be (1 + 1) + (1 + 1)
# = 4.
#
# Example 3:
#
# Input: nums = [0]
#
# Output: 0
#
# Explanation:
#
# We cannot split the array further, so the answer is 0.
#
# Example 4:
#
# Input: nums = [1,-1]
#
# Output: 2
#
# Explanation:
#
# Selecting the whole array gives a total cost of 1 + 1 = 2, which is the
# maximum.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -10^9 <= nums[i] <= 10^9
#

# @lc code=start

from typing import List


class Solution:
    def maximumTotalCost(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Split into subarrays; each subarray cost is + - + - ... Maximize sum.
        At each index, either start a new subarray (+nums[i]) or continue from
        a previous + ending by subtracting nums[i].

        Algorithm:
        - add = max cost ending with +nums[i]; sub ending with -nums[i].
        - Transition: add' = max(add,sub)+x; sub' = add-x.

        Complexity: O(n) time, O(1) space.
        """
        add = nums[0]
        sub = float("-inf")
        for x in nums[1:]:
            add, sub = max(add, sub) + x, add - x
        return max(add, sub)

    def maximumTotalCost_dp(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Array DP form of the same recurrence for clarity.

        Algorithm:
        - dp[i][0]/dp[i][1] for + / - contribution of nums[i].

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        dp0 = [0] * n  # +
        dp1 = [float("-inf")] * n  # -
        dp0[0] = nums[0]
        for i in range(1, n):
            dp0[i] = max(dp0[i - 1], dp1[i - 1]) + nums[i]
            dp1[i] = dp0[i - 1] - nums[i]
        return max(dp0[-1], dp1[-1])
# @lc code=end
