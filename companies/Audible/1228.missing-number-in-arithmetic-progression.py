#
# @lc app=leetcode id=1228 lang=python3
#
# [1228] Missing Number In Arithmetic Progression
#
# https://leetcode.com/problems/missing-number-in-arithmetic-progression/description/
#
# algorithms
# Easy (52.20%)
# Likes:    332
# Dislikes: 45
# Total Accepted:    32.4K
# Total Submissions: 62K
# Testcase Example:  "[5,7,11,13]"
#
#
# In some array arr, the values were in arithmetic progression: the values
# arr[i + 1] - arr[i] are all equal for every 0 <= i < arr.length - 1.
#
# A value from arr was removed that was not the first or last value in the
# array.
#
# Given arr, return the removed value.
#
# Example 1:
#
# Input: arr = [5,7,11,13]
# Output: 9
# Explanation: The previous array was [5,7,9,11,13].
#
# Example 2:
#
# Input: arr = [15,13,12]
# Output: 14
# Explanation: The previous array was [15,14,13,12].
#
# Constraints:
#
# 3 <= arr.length <= 1000
#
# 0 <= arr[i] <= 10^5
#
# The given array is guaranteed to be a valid array.
#
# @lc code=start
from typing import List

class Solution:
    def missingNumber(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Premium. Strictly increasing AP with one missing term. Diff =
        (arr[-1]-arr[0]) / n. Binary search the first position where
        arr[i] != arr[0] + i*diff.

        Algorithm:
        - d = (arr[-1]-arr[0]) // n; binary search mismatch index

        Complexity: O(log n) time, O(1) space.
        """
        n = len(arr)
        d = (arr[-1] - arr[0]) // n
        lo, hi = 0, n - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if arr[mid] == arr[0] + mid * d:
                lo = mid + 1
            else:
                hi = mid
        return arr[0] + lo * d

    def missingNumber_math(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Alternate: expected sum of full AP minus actual sum equals missing.

        Algorithm:
        - d=(last-first)/n; expected = n*(first+last)/2 but with n+1 terms:
          full length n+1; sum_full = (n+1)*(first+last)/2; missing = sum_full-sum(arr)

        Complexity: O(n) time, O(1) space.
        """
        n = len(arr)
        d = (arr[-1] - arr[0]) // n
        return (n + 1) * (arr[0] + arr[-1]) // 2 - sum(arr)
# @lc code=end
