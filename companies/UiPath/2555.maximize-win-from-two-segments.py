#
# @lc app=leetcode id=2555 lang=python3
#
# [2555] Maximize Win From Two Segments
#
# https://leetcode.com/problems/maximize-win-from-two-segments/description/
#
# algorithms
# Medium (38.22%)
# Likes:    608
# Dislikes: 65
# Total Accepted:    16.9K
# Total Submissions: 44.2K
# Testcase Example:  "[1,1,2,2,3,3,5]\n2"
#
# There are some prizes on the X-axis. You are given an integer array
# prizePositions that is sorted in non-decreasing order, where prizePositions[i]
# is the position of the i^th prize. There could be different prizes at the same
# position on the line. You are also given an integer k.
#
# You are allowed to select two segments with integer endpoints. The length of
# each segment must be k. You will collect all prizes whose position falls
# within at least one of the two selected segments (including the endpoints of
# the segments). The two selected segments may intersect.
#
#
# For example if k = 2, you can choose segments [1, 3] and [2, 4], and you will
# win any prize i that satisfies 1 <= prizePositions[i] <= 3 or 2 <=
# prizePositions[i] <= 4.
#
# Return the maximum number of prizes you can win if you choose the two segments
# optimally.
#
#
#
# Example 1:
#
# Input: prizePositions = [1,1,2,2,3,3,5], k = 2
# Output: 7
# Explanation: In this example, you can win all 7 prizes by selecting two
# segments [1, 3] and [3, 5].
#
# Example 2:
#
# Input: prizePositions = [1,2,3,4], k = 0
# Output: 2
# Explanation: For this example, one choice for the segments is [3, 3] and [4,
# 4], and you will be able to get 2 prizes.
#
#
#
# Constraints:
#
#
# 1 <= prizePositions.length <= 10^5
#
#
# 1 <= prizePositions[i] <= 10^9
#
#
# 0 <= k <= 10^9
#
#
# prizePositions is sorted in non-decreasing order.
#

# @lc code=start
from typing import List


class Solution:
    def maximizeWin(self, prizePositions: List[int], k: int) -> int:
        """
        Interview explanation:
        Place two segments of length k on a sorted line of prize positions to cover
        the maximum number of prizes (segments may overlap).

        Algorithm:
        - Sliding window: for each right endpoint j, leftmost i with positions[j]-positions[i]<=k.
        - dp[j+1] = max prizes using one segment among first j positions.
        - Track best = max(dp[i] + window_size ending at j).

        Complexity: O(n) time, O(n) space.
        """
        n = len(prizePositions)
        dp = [0] * (n + 1)
        ans = 0
        i = 0
        for j in range(n):
            while prizePositions[j] - prizePositions[i] > k:
                i += 1
            dp[j + 1] = max(dp[j], j - i + 1)
            ans = max(ans, dp[i] + (j - i + 1))
        return ans
# @lc code=end
