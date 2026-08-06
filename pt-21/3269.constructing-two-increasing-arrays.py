#
# @lc app=leetcode id=3269 lang=python3
#
# [3269] Constructing Two Increasing Arrays
#
# https://leetcode.com/problems/constructing-two-increasing-arrays/description/
#
# algorithms
# Hard (61.58%)
# Likes:    12
# Dislikes: 1
# Total Accepted:    553
# Total Submissions: 898
# Testcase Example:  "[]\n[1,0,1,1]"
#
#
# Given 2 integer arrays nums1 and nums2 consisting only of 0 and 1, your
# task is to calculate the minimum possible largest number in arrays nums1
# and nums2, after doing the following.
#
# Replace every 0 with an even positive integer and every 1 with an odd
# positive integer. After replacement, both arrays should be increasing
# and each integer should be used at most once.
#
# Return the minimum possible largest number after applying the changes.
#
# Example 1:
#
# Input: nums1 = [], nums2 = [1,0,1,1]
#
# Output: 5
#
# Explanation:
#
# After replacing, nums1 = [], and nums2 = [1, 2, 3, 5].
#
# Example 2:
#
# Input: nums1 = [0,1,0,1], nums2 = [1,0,0,1]
#
# Output: 9
#
# Explanation:
#
# One way to replace, having 9 as the largest element is nums1 = [2, 3, 8,
# 9], and nums2 = [1, 4, 6, 7].
#
# Example 3:
#
# Input: nums1 = [0,1,0,0,1], nums2 = [0,0,0,1]
#
# Output: 13
#
# Explanation:
#
# One way to replace, having 13 as the largest element is nums1 = [2, 3,
# 4, 6, 7], and nums2 = [8, 10, 12, 13].
#
# Constraints:
#
# 0 <= nums1.length <= 1000
#
# 1 <= nums2.length <= 1000
#
# nums1 and nums2 consist only of 0 and 1.
#

# @lc code=start

from typing import List


class Solution:
    def minLargest(self, nums1: List[int], nums2: List[int]) -> int:
        """
        Interview explanation:
        Fill both arrays with distinct positives (0→even, 1→odd), each strictly
        increasing; minimize the global maximum. Optimal fill always takes the
        next smallest eligible integer along some interleaving — DP over prefixes.

        Algorithm:
        - dp[i][j] = min achievable max after placing nums1[:i] and nums2[:j].
        - Transition: append next required-parity integer after current max via
          next_num(x, p) = x+1 or x+2 to match parity p.

        Complexity: O(n * m) time, O(n * m) space.
        """
        def next_num(x: int, parity: int) -> int:
            y = x + 1
            if y % 2 != parity:
                y += 1
            return y

        n, m = len(nums1), len(nums2)
        dp = [[0] * (m + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            dp[i][0] = next_num(dp[i - 1][0], nums1[i - 1])
        for j in range(1, m + 1):
            dp[0][j] = next_num(dp[0][j - 1], nums2[j - 1])
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                dp[i][j] = min(
                    next_num(dp[i - 1][j], nums1[i - 1]),
                    next_num(dp[i][j - 1], nums2[j - 1]),
                )
        return dp[n][m]
# @lc code=end
