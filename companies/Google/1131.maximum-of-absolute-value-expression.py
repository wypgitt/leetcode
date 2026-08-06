#
# @lc app=leetcode id=1131 lang=python3
#
# [1131] Maximum of Absolute Value Expression
#
# https://leetcode.com/problems/maximum-of-absolute-value-expression/description/
#
# algorithms
# Medium (48.82%)
# Likes:    683
# Dislikes: 420
# Total Accepted:    31.7K
# Total Submissions: 64.8K
# Testcase Example:  "[1,2,3,4]"
#
# Given two arrays of integers with equal lengths, return the maximum value of:
#
# |arr1[i] - arr1[j]| + |arr2[i] - arr2[j]| + |i - j|
#
# where the maximum is taken over all 0 <= i, j < arr1.length.
#
# Example 1:
#
# Input: arr1 = [1,2,3,4], arr2 = [-1,4,5,6]
# Output: 13
#
# Example 2:
#
# Input: arr1 = [1,-2,-5,0,10], arr2 = [0,-2,-1,-7,-4]
# Output: 20
#
# Constraints:
#
# 2 <= arr1.length == arr2.length <= 40000
#
# -10^6 <= arr1[i], arr2[i] <= 10^6
#

# @lc code=start
from typing import List


class Solution:
    def maxAbsValExpr(self, arr1: List[int], arr2: List[int]) -> int:
        """
        Interview explanation:
        Maximize |arr1[i]-arr1[j]| + |arr2[i]-arr2[j]| + |i-j|.
        Expand absolute values into 8 sign patterns; only 4 unique of form
        ±arr1[i] ± arr2[i] ± i; answer is max(max-min) over each pattern.

        Algorithm:
        - For each of 4 sign combos of (arr1, arr2, index), track max-min of
          arr1[i]*s1 + arr2[i]*s2 + i*s3 with s3=1 (index absorbed in signs).

        Complexity: O(n) time, O(1) space.
        """
        n = len(arr1)
        ans = 0
        for s1, s2 in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            mx = float("-inf")
            mn = float("inf")
            for i in range(n):
                v = s1 * arr1[i] + s2 * arr2[i] + i
                mx = max(mx, v)
                mn = min(mn, v)
            ans = max(ans, mx - mn)
        return int(ans)
# @lc code=end
