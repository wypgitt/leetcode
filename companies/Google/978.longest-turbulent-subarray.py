#
# @lc app=leetcode id=978 lang=python3
#
# [978] Longest Turbulent Subarray
#
# https://leetcode.com/problems/longest-turbulent-subarray/description/
#
# algorithms
# Medium (49.38%)
# Likes:    2133
# Dislikes: 263
# Total Accepted:    145K
# Total Submissions: 294K
# Testcase Example:  "[9,4,2,10,7,8,8,1,9]"
#
# Given an integer array arr, return the length of a maximum size turbulent
# subarray of arr.
#
# A subarray is turbulent if the comparison sign flips between each adjacent
# pair of elements in the subarray.
#
# More formally, a subarray [arr[i], arr[i + 1], ..., arr[j]] of arr is said to
# be turbulent if and only if:
#
# For i <= k < j:
#
# arr[k] > arr[k + 1] when k is odd, and
#
# arr[k] < arr[k + 1] when k is even.
#
# Or, for i <= k < j:
#
# arr[k] > arr[k + 1] when k is even, and
#
# arr[k] < arr[k + 1] when k is odd.
#
# Example 1:
#
# Input: arr = [9,4,2,10,7,8,8,1,9]
# Output: 5
# Explanation: arr[1] > arr[2] < arr[3] > arr[4] < arr[5]
#
# Example 2:
#
# Input: arr = [4,8,12,16]
# Output: 2
#
# Example 3:
#
# Input: arr = [100]
# Output: 1
#
# Constraints:
#
# 1 <= arr.length <= 4 * 10^4
#
# 0 <= arr[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def maxTurbulenceSize(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Turbulent means adjacent comparisons strictly alternate (> then < then
        > ...). Track current run length; extend when the new comparison flips
        relative to the previous one; reset to 2 (or 1 if equal) otherwise.

        Algorithm:
        - ans = cur = 1.
        - For i in 1..n-1: compare arr[i-1] vs arr[i].
          If equal: cur = 1.
          Elif i==1 or sign flips vs previous pair: cur += 1.
          Else: cur = 2.
          ans = max(ans, cur).

        Complexity: O(n) time, O(1) space.
        """
        n = len(arr)
        ans = 1
        cur = 1
        for i in range(1, n):
            if arr[i] == arr[i - 1]:
                cur = 1
            elif i == 1 or (arr[i] - arr[i - 1]) * (arr[i - 1] - arr[i - 2]) < 0:
                cur += 1
            else:
                cur = 2
            ans = max(ans, cur)
        return ans

    def maxTurbulenceSize_dp(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Alternate DP: up[i] = longest turbulent ending at i with arr[i-1] < arr[i];
        down[i] similarly for >. Transition flips the direction.

        Algorithm:
        - up=down=1; ans=1.
        - If arr[i]>arr[i-1]: up = down+1; down=1.
          Elif arr[i]<arr[i-1]: down = up+1; up=1.
          Else: up=down=1.
        - Track max(up, down).

        Complexity: O(n) time, O(1) space.
        """
        ans = 1
        up = down = 1
        for i in range(1, len(arr)):
            if arr[i] > arr[i - 1]:
                up = down + 1
                down = 1
            elif arr[i] < arr[i - 1]:
                down = up + 1
                up = 1
            else:
                up = down = 1
            ans = max(ans, up, down)
        return ans
# @lc code=end
