#
# @lc app=leetcode id=1959 lang=python3
#
# [1959] Minimum Total Space Wasted With K Resizing Operations
#
# https://leetcode.com/problems/minimum-total-space-wasted-with-k-resizing-operations/description/
#
# algorithms
# Medium (44.13%)
# Likes:    600
# Dislikes: 64
# Total Accepted:    11.6K
# Total Submissions: 26.3K
# Testcase Example:  "[10,20]"
#
# You are currently designing a dynamic array. You are given a 0-indexed
# integer array nums, where nums[i] is the number of elements that will be in
# the array at time i. In addition, you are given an integer k, the maximum
# number of times you can resize the array (to any size).
#
# The size of the array at time t, size_t, must be at least nums[t] because
# there needs to be enough space in the array to hold all the elements. The
# space wasted at time t is defined as size_t - nums[t], and the total space
# wasted is the sum of the space wasted across every time t where 0 <= t <
# nums.length.
#
# Return the minimum total space wasted if you can resize the array at most k
# times.
#
# Note: The array can have any size at the start and does not count towards the
# number of resizing operations.
#
# Example 1:
#
# Input: nums = [10,20], k = 0
# Output: 10
# Explanation: size = [20,20].
# We can set the initial size to be 20.
# The total wasted space is (20 - 10) + (20 - 20) = 10.
#
# Example 2:
#
# Input: nums = [10,20,30], k = 1
# Output: 10
# Explanation: size = [20,20,30].
# We can set the initial size to be 20 and resize to 30 at time 2.
# The total wasted space is (20 - 10) + (20 - 20) + (30 - 30) = 10.
#
# Example 3:
#
# Input: nums = [10,20,15,30,20], k = 2
# Output: 15
# Explanation: size = [10,20,20,30,30].
# We can set the initial size to 10, resize to 20 at time 1, and resize to 30
# at time 3.
# The total wasted space is (10 - 10) + (20 - 20) + (20 - 15) + (30 - 30) + (30
# - 20) = 15.
#
# Constraints:
#
# 1 <= nums.length <= 200
#
# 1 <= nums[i] <= 10^6
#
# 0 <= k <= nums.length - 1
#

# @lc code=start
from typing import List


class Solution:
    def minSpaceWastedKResizing(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Split array into at most k+1 contiguous segments; each segment wastes
        (max-of-seg)*len - sum. Minimize total waste via DP.

        Algorithm:
        - dp[i][j] = min waste for nums[:i] with j resizes (j+1 segments).
        - Precompute cost(l,r) = max[l:r]*len - sum[l:r].
        - Transition: dp[i][j] = min over t < i of dp[t][j-1] + cost(t,i).

        Complexity: O(n^2 * k) time, O(n*k) space.
        """
        n = len(nums)
        INF = 10**18
        cost = [[0] * (n + 1) for _ in range(n)]
        for i in range(n):
            mx = 0
            s = 0
            for j in range(i, n):
                mx = max(mx, nums[j])
                s += nums[j]
                cost[i][j + 1] = mx * (j - i + 1) - s

        dp = [[INF] * (k + 2) for _ in range(n + 1)]
        dp[0][0] = 0
        for i in range(1, n + 1):
            for j in range(1, min(i, k + 1) + 1):
                for t in range(j - 1, i):
                    dp[i][j] = min(dp[i][j], dp[t][j - 1] + cost[t][i])
        return int(min(dp[n][1: k + 2]))

    def minSpaceWastedKResizing_rolling(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate DP with the same recurrence; iterate segments explicitly.

        Algorithm:
        - Same cost table; fill by number of segments.

        Complexity: O(n^2 * k) time, O(n*k) space.
        """
        n = len(nums)
        INF = 10**18
        # dp[seg][i]: first i elements, seg segments
        dp = [[INF] * (n + 1) for _ in range(k + 2)]
        dp[0][0] = 0
        for seg in range(1, k + 2):
            for i in range(seg, n + 1):
                mx = 0
                s = 0
                for t in range(i - 1, seg - 2, -1):
                    mx = max(mx, nums[t])
                    s += nums[t]
                    dp[seg][i] = min(dp[seg][i], dp[seg - 1][t] + mx * (i - t) - s)
        return int(min(dp[seg][n] for seg in range(1, k + 2)))
# @lc code=end

