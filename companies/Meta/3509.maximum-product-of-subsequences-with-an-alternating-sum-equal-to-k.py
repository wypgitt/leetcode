#
# @lc app=leetcode id=3509 lang=python3
#
# [3509] Maximum Product of Subsequences With an Alternating Sum Equal to K
#
# https://leetcode.com/problems/maximum-product-of-subsequences-with-an-alternating-sum-equal-to-k/description/
#
# algorithms
# Hard (13.82%)
# Likes:    59
# Dislikes: 6
# Total Accepted:    6.8K
# Total Submissions: 49.2K
# Testcase Example:  "[1,2,3]\n2\n10"
#
#
# You are given an integer array nums and two integers, k and limit. Your
# task is to find a non-empty subsequence of nums that:
#
# Has an alternating sum equal to k.
#
# Maximizes the product of all its numbers without the product exceeding
# limit.
#
# Return the product of the numbers in such a subsequence. If no
# subsequence satisfies the requirements, return -1.
#
# The alternating sum of a 0-indexed array is defined as the sum of the
# elements at even indices minus the sum of the elements at odd indices.
#
# Example 1:
#
# Input: nums = [1,2,3], k = 2, limit = 10
#
# Output: 6
#
# Explanation:
#
# The subsequences with an alternating sum of 2 are:
#
# [1, 2, 3]
#
# Alternating Sum: 1 - 2 + 3 = 2
#
# Product: 1 * 2 * 3 = 6
#
# [2]
#
# Alternating Sum: 2
#
# Product: 2
#
# The maximum product within the limit is 6.
#
# Example 2:
#
# Input: nums = [0,2,3], k = -5, limit = 12
#
# Output: -1
#
# Explanation:
#
# A subsequence with an alternating sum of exactly -5 does not exist.
#
# Example 3:
#
# Input: nums = [2,2,3,3], k = 0, limit = 9
#
# Output: 9
#
# Explanation:
#
# The subsequences with an alternating sum of 0 are:
#
# [2, 2]
#
# Alternating Sum: 2 - 2 = 0
#
# Product: 2 * 2 = 4
#
# [3, 3]
#
# Alternating Sum: 3 - 3 = 0
#
# Product: 3 * 3 = 9
#
# [2, 2, 3, 3]
#
# Alternating Sum: 2 - 2 + 3 - 3 = 0
#
# Product: 2 * 2 * 3 * 3 = 36
#
# The subsequence [2, 2, 3, 3] has the greatest product with an
# alternating sum equal to k, but 36 > 9. The next greatest product is 9,
# which is within the limit.
#
# Constraints:
#
# 1 <= nums.length <= 150
#
# 0 <= nums[i] <= 12
#
# -10^5 <= k <= 10^5
#
# 1 <= limit <= 5000
#

# @lc code=start
from typing import List
import functools


class Solution:
    def maxProduct(self, nums: List[int], k: int, limit: int) -> int:
        """
        Interview explanation:
        Choose a non-empty subsequence with alternating sum = k and maximum
        product <= limit. nums[i] and limit are small — DFS + memo on
        (index, remaining k, capped product, parity state).

        Algorithm:
        - States: FIRST (not started), next subtract, next add.
        - Cap product at limit+1; skip or take each element with sign by state.
        - Return best product for remaining k == 0 after taking something.

        Complexity: O(n * |k| * limit) states; fine for given constraints.
        """
        MIN = -5000
        if abs(k) > sum(nums):
            return -1

        @functools.lru_cache(None)
        def dp(i: int, product: int, state: int, rem: int) -> int:
            if i == len(nums):
                return product if rem == 0 and state != 0 and product <= limit else MIN
            res = dp(i + 1, product, state, rem)
            if state == 0:
                res = max(res, dp(i + 1, nums[i], 1, rem - nums[i]))
            elif state == 1:
                res = max(
                    res,
                    dp(i + 1, min(product * nums[i], limit + 1), 2, rem + nums[i]),
                )
            else:
                res = max(
                    res,
                    dp(i + 1, min(product * nums[i], limit + 1), 1, rem - nums[i]),
                )
            return res

        ans = dp(0, 1, 0, k)
        return -1 if ans == MIN else ans
# @lc code=end
