#
# @lc app=leetcode id=3473 lang=python3
#
# [3473] Sum of K Subarrays With Length at Least M
#
# https://leetcode.com/problems/sum-of-k-subarrays-with-length-at-least-m/description/
#
# algorithms
# Medium (26.03%)
# Likes:    97
# Dislikes: 16
# Total Accepted:    8.5K
# Total Submissions: 32.6K
# Testcase Example:  "[1,2,-1,3,3,4]\n2\n2"
#
#
# You are given an integer array nums and two integers, k and m.
#
# Return the maximum sum of k non-overlapping subarrays of nums, where
# each subarray has a length of at least m.
#
# Example 1:
#
# Input: nums = [1,2,-1,3,3,4], k = 2, m = 2
#
# Output: 13
#
# Explanation:
#
# The optimal choice is:
#
# Subarray nums[3..5] with sum 3 + 3 + 4 = 10 (length is 3 >= m).
#
# Subarray nums[0..1] with sum 1 + 2 = 3 (length is 2 >= m).
#
# The total sum is 10 + 3 = 13.
#
# Example 2:
#
# Input: nums = [-10,3,-1,-2], k = 4, m = 1
#
# Output: -10
#
# Explanation:
#
# The optimal choice is choosing each element as a subarray. The output is
# (-10) + 3 + (-1) + (-2) = -10.
#
# Constraints:
#
# 1 <= nums.length <= 2000
#
# -10^4 <= nums[i] <= 10^4
#
# 1 <= k <= floor(nums.length / m)
#
# 1 <= m <= 3
#

# @lc code=start
import functools
import itertools
from typing import List


class Solution:
    def maxSum(self, nums: List[int], k: int, m: int) -> int:
        """
        Interview explanation:
        Choose k non-overlapping subarrays each of length >= m maximizing sum.
        DP with a flag for whether we are currently extending a segment.

        Algorithm:
        - dp(i, ongoing, rem): best from index i with rem segments left.
        - ongoing=0: skip i, or start a length-m block then enter ongoing=1.
        - ongoing=1: end segment (to ongoing=0) or extend by taking nums[i].

        Complexity: O(n k) time/space (m <= 3 helps constants).
        """
        INF = 20_000_000
        n = len(nums)
        prefix = list(itertools.accumulate(nums, initial=0))

        @functools.lru_cache(None)
        def dp(i: int, ongoing: int, rem: int) -> int:
            if rem < 0:
                return -INF
            if i == n:
                return 0 if rem == 0 else -INF
            if ongoing == 1:
                return max(dp(i, 0, rem), dp(i + 1, 1, rem) + nums[i])
            res = dp(i + 1, 0, rem)
            if i + m <= n:
                res = max(
                    res,
                    dp(i + m, 1, rem - 1) + (prefix[i + m] - prefix[i]),
                )
            return res

        return dp(0, 0, k)
# @lc code=end

