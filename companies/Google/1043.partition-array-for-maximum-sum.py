#
# @lc app=leetcode id=1043 lang=python3
#
# [1043] Partition Array for Maximum Sum
#
# https://leetcode.com/problems/partition-array-for-maximum-sum/description/
#
# algorithms
# Medium (77.53%)
# Likes:    5132
# Dislikes: 438
# Total Accepted:    283K
# Total Submissions: 365K
# Testcase Example:  "[1,15,7,9,2,5,10]"
#
# Given an integer array arr, partition the array into (contiguous) subarrays
# of length at most k. After partitioning, each subarray has their values
# changed to become the maximum value of that subarray.
#
# Return the largest sum of the given array after partitioning. Test cases are
# generated so that the answer fits in a 32-bit integer.
#
# Example 1:
#
# Input: arr = [1,15,7,9,2,5,10], k = 3
# Output: 84
# Explanation: arr becomes [15,15,15,9,10,10,10]
#
# Example 2:
#
# Input: arr = [1,4,1,5,7,3,6,1,9,9,3], k = 4
# Output: 83
#
# Example 3:
#
# Input: arr = [1], k = 1
# Output: 1
#
# Constraints:
#
# 1 <= arr.length <= 500
#
# 0 <= arr[i] <= 10^9
#
# 1 <= k <= arr.length
#

# @lc code=start
from typing import List


class Solution:
    def maxSumAfterPartitioning(self, arr: List[int], k: int) -> int:
        """
        Interview explanation:
        DP: dp[i] = max sum for prefix arr[:i]. Last partition ending at i-1 of
        length L=1..k has value max(arr[i-L:i])*L + dp[i-L].

        Algorithm:
        - dp[0]=0
        - For i=1..n: mx=0; for L=1..min(k,i): mx=max(mx,arr[i-L]);
          dp[i]=max(dp[i], dp[i-L]+mx*L)

        Complexity: O(n*k) time, O(n) space.
        """
        n = len(arr)
        dp = [0] * (n + 1)
        for i in range(1, n + 1):
            mx = 0
            for L in range(1, min(k, i) + 1):
                mx = max(mx, arr[i - L])
                dp[i] = max(dp[i], dp[i - L] + mx * L)
        return dp[n]

    def maxSumAfterPartitioning_memo(self, arr: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate top-down memo: dfs(i) max sum from index i onward.

        Algorithm:
        - dfs(i): try partitions of length 1..k starting at i

        Complexity: O(n*k) time, O(n) space.
        """
        from functools import lru_cache

        n = len(arr)

        @lru_cache(None)
        def dfs(i: int) -> int:
            if i >= n:
                return 0
            mx = best = 0
            for L in range(1, min(k, n - i) + 1):
                mx = max(mx, arr[i + L - 1])
                best = max(best, mx * L + dfs(i + L))
            return best

        return dfs(0)
# @lc code=end
