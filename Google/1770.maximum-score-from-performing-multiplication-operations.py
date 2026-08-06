#
# @lc app=leetcode id=1770 lang=python3
#
# [1770] Maximum Score from Performing Multiplication Operations
#
# https://leetcode.com/problems/maximum-score-from-performing-multiplication-operations/description/
#
# algorithms
# Hard (43.54%)
# Likes:    2605
# Dislikes: 514
# Total Accepted:    137K
# Total Submissions: 316K
# Testcase Example:  "[1,2,3]"
#
# You are given two 0-indexed integer arrays nums and multipliers of size n and
# m respectively, where n >= m.
#
# You begin with a score of 0. You want to perform exactly m operations. On the
# i^th operation (0-indexed) you will:
#
# Choose one integer x from either the start or the end of the array nums.
#
# Add multipliers[i] * x to your score.
#
# Note that multipliers[0] corresponds to the first operation, multipliers[1]
# to the second operation, and so on.
#
# Remove x from nums.
#
# Return the maximum score after performing m operations.
#
# Example 1:
#
# Input: nums = [1,2,3], multipliers = [3,2,1]
# Output: 14
# Explanation: An optimal solution is as follows:
# - Choose from the end, [1,2,3], adding 3 * 3 = 9 to the score.
# - Choose from the end, [1,2], adding 2 * 2 = 4 to the score.
# - Choose from the end, [1], adding 1 * 1 = 1 to the score.
# The total score is 9 + 4 + 1 = 14.
#
# Example 2:
#
# Input: nums = [-5,-3,-3,-2,7,1], multipliers = [-10,-5,3,4,6]
# Output: 102
# Explanation: An optimal solution is as follows:
# - Choose from the start, [-5,-3,-3,-2,7,1], adding -5 * -10 = 50 to the
# score.
# - Choose from the start, [-3,-3,-2,7,1], adding -3 * -5 = 15 to the score.
# - Choose from the start, [-3,-2,7,1], adding -3 * 3 = -9 to the score.
# - Choose from the end, [-2,7,1], adding 1 * 4 = 4 to the score.
# - Choose from the end, [-2,7], adding 7 * 6 = 42 to the score.
# The total score is 50 + 15 - 9 + 4 + 42 = 102.
#
# Constraints:
#
# n == nums.length
#
# m == multipliers.length
#
# 1 <= m <= 300
#
# m <= n <= 10^5
#
# -1000 <= nums[i], multipliers[i] <= 1000
#

# @lc code=start
from typing import List
from functools import lru_cache


class Solution:
    def maximumScore(self, nums: List[int], multipliers: List[int]) -> int:
        """
        Interview explanation:
        m operations; each takes nums from left or right end * multipliers[op].
        DP on how many left picks (right derived). dp[i][left] after i ops with
        `left` taken from front.

        Algorithm:
        - m=len(multipliers), n=len(nums).
        - dp[i][l] = max score with i ops done and l left-picks
          = max(nums[l-1]*mult + prev, nums[n-(i-l)]*mult + prev_right).
        - Iterate ops bottom-up or top-down memo.

        Complexity: O(m^2) time and space.
        """
        n, m = len(nums), len(multipliers)
        # dp[left] after processing op operations (rolling)
        dp = [0] * (m + 1)
        for op in range(m - 1, -1, -1):
            ndp = [0] * (m + 1)
            for left in range(op + 1):
                right = n - 1 - (op - left)
                mult = multipliers[op]
                ndp[left] = max(
                    nums[left] * mult + dp[left + 1],
                    nums[right] * mult + dp[left],
                )
            dp = ndp
        return dp[0]

    def maximumScore_memo(self, nums: List[int], multipliers: List[int]) -> int:
        """
        Interview explanation:
        Alternate top-down: state (op, left); right = n-1-(op-left); choose left/right end.

        Algorithm:
        - @lru_cache dfs(op, left); base op==m → 0.

        Complexity: O(m^2) time and space.
        """
        n, m = len(nums), len(multipliers)

        @lru_cache(None)
        def dfs(op: int, left: int) -> int:
            if op == m:
                return 0
            right = n - 1 - (op - left)
            mult = multipliers[op]
            return max(
                nums[left] * mult + dfs(op + 1, left + 1),
                nums[right] * mult + dfs(op + 1, left),
            )

        return dfs(0, 0)
# @lc code=end
