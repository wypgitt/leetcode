#
# @lc app=leetcode id=2501 lang=python3
#
# [2501] Longest Square Streak in an Array
#
# https://leetcode.com/problems/longest-square-streak-in-an-array/description/
#
# algorithms
# Medium (53.10%)
# Likes:    1012
# Dislikes: 34
# Total Accepted:    157.2K
# Total Submissions: 296.1K
# Testcase Example:  "[4,3,6,16,8,2]"
#
# You are given an integer array nums. A subsequence of nums is called a square
# streak if:
#
#
# The length of the subsequence is at least 2, and
#
#
# after sorting the subsequence, each element (except the first element) is the
# square of the previous number.
#
# Return the length of the longest square streak in nums, or return -1 if there
# is no square streak.
#
# A subsequence is an array that can be derived from another array by deleting
# some or no elements without changing the order of the remaining elements.
#
#
#
# Example 1:
#
# Input: nums = [4,3,6,16,8,2]
# Output: 3
# Explanation: Choose the subsequence [4,16,2]. After sorting it, it becomes
# [2,4,16].
# - 4 = 2 * 2.
# - 16 = 4 * 4.
# Therefore, [4,16,2] is a square streak.
# It can be shown that every subsequence of length 4 is not a square streak.
#
# Example 2:
#
# Input: nums = [2,3,5,6,7]
# Output: -1
# Explanation: There is no square streak in nums so return -1.
#
#
#
# Constraints:
#
#
# 2 <= nums.length <= 10^5
#
#
# 2 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def longestSquareStreak(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Longest subsequence that, after sorting, forms x, x^2, x^4, ... with
        length >= 2; else -1.

        Algorithm:
        - Put unique values in a set; for each start, walk cur -> cur*cur while
          present; track max chain length.

        Complexity: O(n log M) time (chains are short), O(n) space.
        """
        s = set(nums)
        ans = -1
        for x in s:
            length = 1
            cur = x
            while cur <= 10**5 and cur * cur in s:
                cur *= cur
                length += 1
            if length >= 2:
                ans = max(ans, length)
        return ans

    def longestSquareStreak_dp(self, nums: List[int]) -> int:
        """
        Interview explanation:
        DP on sorted unique values: streak ending at x extends from sqrt(x).

        Algorithm:
        - Sort unique; for each x, if perfect square root r is in map, dp[x] =
          dp[r]+1; else 1. Answer max dp if >= 2 else -1.

        Complexity: O(n log n) time, O(n) space.
        """
        uniq = sorted(set(nums))
        dp = {}
        best = 1
        for x in uniq:
            r = int(x**0.5)
            if r * r == x and r in dp:
                dp[x] = dp[r] + 1
            else:
                dp[x] = 1
            best = max(best, dp[x])
        return best if best >= 2 else -1
# @lc code=end
