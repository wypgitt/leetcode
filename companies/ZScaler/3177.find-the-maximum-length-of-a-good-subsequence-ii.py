#
# @lc app=leetcode id=3177 lang=python3
#
# [3177] Find the Maximum Length of a Good Subsequence II
#
# https://leetcode.com/problems/find-the-maximum-length-of-a-good-subsequence-ii/description/
#
# algorithms
# Hard (25.24%)
# Likes:    148
# Dislikes: 10
# Total Accepted:    10.1K
# Total Submissions: 40.2K
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
# 1 <= nums.length <= 5 * 10^3
#
# 1 <= nums[i] <= 10^9
#
# 0 <= k <= min(50, nums.length)
#

# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def maximumLength(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Same "at most k adjacent changes" as I, but n <= 5e3 so drop the j-loop.
        Track, for each change budget, best length ending on each value and the
        global best for that budget.

        Algorithm:
        - dp[t][val] = best length with at most t changes ending with val.
        - For value x: extend dp[t][x], or take max_dp[t-1]+1 (new change).
        - Compute candidates from old state, then write back.

        Complexity: O(n * k) time, O(n * k) space worst-case on maps.
        """
        # dp[t][val] / max_dp[t]: best with at most t changes
        dp: list[dict[int, int]] = [defaultdict(int) for _ in range(k + 1)]
        max_dp = [0] * (k + 1)
        for x in nums:
            cand = [0] * (k + 1)
            for t in range(k + 1):
                cur = dp[t][x] + 1
                if t > 0:
                    cur = max(cur, max_dp[t - 1] + 1)
                cand[t] = cur
            for t in range(k + 1):
                if cand[t] > dp[t][x]:
                    dp[t][x] = cand[t]
                if t:
                    dp[t][x] = max(dp[t][x], dp[t - 1][x])
                max_dp[t] = max(max_dp[t], dp[t][x])
            for t in range(1, k + 1):
                max_dp[t] = max(max_dp[t], max_dp[t - 1])
        return max_dp[k]

    def maximumLength_descending(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: update change-layers from high to low in place so the current
        element is not reused within the same step.

        Algorithm:
        - For t from k..0: dp[t][x] = max(dp[t][x]+1, max_dp[t-1]+1); refresh max_dp.

        Complexity: O(n * k) time, O(n * k) space.
        """
        dp: list[dict[int, int]] = [defaultdict(int) for _ in range(k + 1)]
        max_dp = [0] * (k + 1)
        for x in nums:
            for t in range(k, -1, -1):
                cur = dp[t][x] + 1
                if t:
                    cur = max(cur, max_dp[t - 1] + 1)
                dp[t][x] = cur
                max_dp[t] = max(max_dp[t], cur)
            for t in range(1, k + 1):
                max_dp[t] = max(max_dp[t], max_dp[t - 1])
        return max_dp[k]
# @lc code=end
