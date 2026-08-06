#
# @lc app=leetcode id=3409 lang=python3
#
# [3409] Longest Subsequence With Decreasing Adjacent Difference
#
# https://leetcode.com/problems/longest-subsequence-with-decreasing-adjacent-difference/description/
#
# algorithms
# Medium (16.90%)
# Likes:    153
# Dislikes: 25
# Total Accepted:    7.6K
# Total Submissions: 45K
# Testcase Example:  "[16,6,3]"
#
#
# You are given an array of integers nums.
#
# Your task is to find the length of the longest subsequence seq of nums,
# such that the absolute differences between consecutive elements form a
# non-increasing sequence of integers. In other words, for a subsequence
# seq_0, seq_1, seq_2, ..., seq_m of nums, |seq_1 - seq_0| >= |seq_2 -
# seq_1| >= ... >= |seq_m - seq_m - 1|.
#
# Return the length of such a subsequence.
#
# Example 1:
#
# Input: nums = [16,6,3]
#
# Output: 3
#
# Explanation:
#
# The longest subsequence is [16, 6, 3] with the absolute adjacent
# differences [10, 3].
#
# Example 2:
#
# Input: nums = [6,5,3,4,2,1]
#
# Output: 4
#
# Explanation:
#
# The longest subsequence is [6, 4, 2, 1] with the absolute adjacent
# differences [2, 2, 1].
#
# Example 3:
#
# Input: nums = [10,20,10,19,10,20]
#
# Output: 5
#
# Explanation:
#
# The longest subsequence is [10, 20, 10, 19, 10] with the absolute
# adjacent differences [10, 10, 9, 9].
#
# Constraints:
#
# 2 <= nums.length <= 10^4
#
# 1 <= nums[i] <= 300
#

# @lc code=start
from typing import List


class Solution:
    def longestSubsequence(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Longest subsequence whose adjacent absolute differences are
        non-increasing. Values are in [1,300], so DP on (value, last_diff).

        Algorithm:
        - dp[v][d] = best length ending at value v with last diff >= d
          (after suffix-max).
        - For each num, for each prev: extend with diff=|num-prev| using
          dp[prev][diff]; then suffix-max dp[num].

        Complexity: O(n * M) time, O(M^2) space where M = max(nums) <= 300.
        """
        mx = max(nums)
        dp = [[0] * (mx + 1) for _ in range(mx + 1)]

        for num in nums:
            for prev in range(1, mx + 1):
                diff = abs(num - prev)
                dp[num][diff] = max(dp[num][diff], dp[prev][diff] + 1)
            for j in range(mx - 1, -1, -1):
                dp[num][j] = max(dp[num][j], dp[num][j + 1])

        return max(row[0] for row in dp)
# @lc code=end
