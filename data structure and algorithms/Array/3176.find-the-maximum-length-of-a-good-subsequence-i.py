#
# @lc app=leetcode id=3176 lang=python3
#
# [3176] Find the Maximum Length of a Good Subsequence I
#
# https://leetcode.com/problems/find-the-maximum-length-of-a-good-subsequence-i/description/
#
# algorithms
# Medium (32.88%)
# Likes:    172
# Dislikes: 102
# Total Accepted:    24.4K
# Total Submissions: 74.2K
# Testcase Example:  "[1,2,1,1,3]\n2"
#
#
# You are given an integer array nums and a non-negative integer k. A
# sequence of integers seq is called good if there are at most k indices i
# in the range [0, seq.length - 2] such that seq[i] != seq[i + 1].
#
# Return the maximum possible length of a good subsequence of nums.
#
# Example 1:
#
# Input: nums = [1,2,1,1,3], k = 2
#
# Output: 4
#
# Explanation:
#
# The maximum length subsequence is [1,2,1,1,3].
#
# Example 2:
#
# Input: nums = [1,2,3,4,5,1], k = 0
#
# Output: 2
#
# Explanation:
#
# The maximum length subsequence is [1,2,3,4,5,1].
#
# Constraints:
#
# 1 <= nums.length <= 500
#
# 1 <= nums[i] <= 10^9
#
# 0 <= k <= min(nums.length, 25)
#

# @lc code=start
from typing import List


class Solution:
    def maximumLength(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        A good subsequence has at most k adjacent value-changes. n <= 500 and
        k <= 25, so DP over ending index and used changes works.

        Algorithm:
        - dp[i][t] = max length ending at i with exactly t changes.
        - From j < i: same value keeps t; different goes to t+1 (if t+1 <= k).
        - Answer is max over all dp[i][t] for t <= k.

        Complexity: O(n^2 * k) time, O(n * k) space.
        """
        n = len(nums)
        # dp[i][t] = best length ending at i with exactly t changes
        dp = [[1] + [0] * k for _ in range(n)]
        ans = 1
        for i in range(n):
            for j in range(i):
                if nums[j] == nums[i]:
                    for t in range(k + 1):
                        if dp[j][t]:
                            dp[i][t] = max(dp[i][t], dp[j][t] + 1)
                else:
                    for t in range(k):
                        if dp[j][t]:
                            dp[i][t + 1] = max(dp[i][t + 1], dp[j][t] + 1)
            ans = max(ans, max(dp[i]))
        return ans

    def maximumLength_at_most(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: dp[i][t] = best ending at i with at most t changes; enforce
        monotonicity across t after transitions.

        Algorithm:
        - Same / different transitions; then dp[i][t] = max(dp[i][t], dp[i][t-1]).

        Complexity: O(n^2 * k) time, O(n * k) space.
        """
        n = len(nums)
        dp = [[1] * (k + 1) for _ in range(n)]
        ans = 1
        for i in range(n):
            for t in range(k + 1):
                for j in range(i):
                    if nums[j] == nums[i]:
                        dp[i][t] = max(dp[i][t], dp[j][t] + 1)
                    elif t > 0:
                        dp[i][t] = max(dp[i][t], dp[j][t - 1] + 1)
                if t:
                    dp[i][t] = max(dp[i][t], dp[i][t - 1])
                ans = max(ans, dp[i][t])
        return ans
# @lc code=end
