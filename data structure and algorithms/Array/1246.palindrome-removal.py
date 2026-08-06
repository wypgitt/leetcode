#
# @lc app=leetcode id=1246 lang=python3
#
# [1246] Palindrome Removal
#
# https://leetcode.com/problems/palindrome-removal/description/
#
# algorithms
# Hard (46.19%)
# Likes:    319
# Dislikes: 14
# Total Accepted:    12.1K
# Total Submissions: 26.2K
# Testcase Example:  "[1,2]"
#
#
# You are given an integer array arr.
#
# In one move, you can select a palindromic subarray arr[i], arr[i + 1],
# ..., arr[j] where i <= j, and remove that subarray from the given array.
# Note that after removing a subarray, the elements on the left and on the
# right of that subarray move to fill the gap left by the removal.
#
# Return the minimum number of moves needed to remove all numbers from the
# array.
#
# Example 1:
#
# Input: arr = [1,2]
# Output: 2
#
# Example 2:
#
# Input: arr = [1,3,4,1,5]
# Output: 3
# Explanation: Remove [4] then remove [1,3,1] then remove [5].
#
# Constraints:
#
# 1 <= arr.length <= 100
#
# 1 <= arr[i] <= 20
#
# @lc code=start
from typing import List

class Solution:
    def minimumMoves(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Premium. Remove palindromic subarrays; min moves to clear array.
        Interval DP: dp[i][j] = min moves to remove arr[i..j].
        If arr[i]==arr[j], can merge with inner; also try all splits.

        Algorithm:
        - dp[i][i]=1; for len: dp[i][j]=min over k of dp[i][k]+dp[k+1][j]
        - if arr[i]==arr[j]: dp[i][j]=min(dp[i][j], dp[i+1][j-1]) (or 1 if len=2)

        Complexity: O(n^3) time, O(n^2) space.
        """
        n = len(arr)
        dp = [[0] * n for _ in range(n)]
        for i in range(n):
            dp[i][i] = 1
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                dp[i][j] = dp[i + 1][j] + 1  # remove arr[i] alone then rest
                if arr[i] == arr[i + 1]:
                    dp[i][j] = min(dp[i][j], (dp[i + 2][j] if i + 2 <= j else 1))
                for k in range(i + 2, j + 1):
                    if arr[i] == arr[k]:
                        dp[i][j] = min(dp[i][j], dp[i + 1][k - 1] + (dp[k + 1][j] if k + 1 <= j else 0))
                # also standard split
                for k in range(i, j):
                    dp[i][j] = min(dp[i][j], dp[i][k] + dp[k + 1][j])
        return dp[0][n - 1]
# @lc code=end
