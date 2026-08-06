#
# @lc app=leetcode id=1287 lang=python3
#
# [1287] Element Appearing More Than 25% In Sorted Array
#
# https://leetcode.com/problems/element-appearing-more-than-25-in-sorted-array/description/
#
# algorithms
# Easy (61.33%)
# Likes:    1792
# Dislikes: 85
# Total Accepted:    265K
# Total Submissions: 432K
# Testcase Example:  "[1,2,2,6,6,6,6,7,10]"
#
# Given an integer array sorted in non-decreasing order, there is exactly one
# integer in the array that occurs more than 25% of the time, return that
# integer.
#
# Example 1:
#
# Input: arr = [1,2,2,6,6,6,6,7,10]
# Output: 6
#
# Example 2:
#
# Input: arr = [1,1]
# Output: 1
#
# Constraints:
#
# 1 <= arr.length <= 10^4
#
# 0 <= arr[i] <= 10^5
#

# @lc code=start

from typing import List


class Solution:
    def findSpecialInteger(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Sorted array; the element appearing >25% must occupy a span of length
        > n/4. Check arr[i]==arr[i+n//4] for i in range; first hit is answer.
        Also binary search bounds per candidate.

        Algorithm:
        - span = n//4; for i in 0..n-span-1: if arr[i]==arr[i+span] return it.

        Complexity: O(n) time, O(1) space.
        """
        n = len(arr)
        span = n // 4
        for i in range(n - span):
            if arr[i] == arr[i + span]:
                return arr[i]
        return arr[0]

    def findSpecialInteger_binary(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Alternate: for candidates at 0, n/4, n/2, 3n/4 use bisect to count
        frequency; return if > n/4.

        Algorithm:
        - For idx in [0,n//4,n//2,3*n//4]: count with bisect; check threshold.

        Complexity: O(log n) time, O(1) space.
        """
        import bisect

        n = len(arr)
        for idx in (0, n // 4, n // 2, 3 * n // 4):
            x = arr[idx]
            left = bisect.bisect_left(arr, x)
            right = bisect.bisect_right(arr, x)
            if right - left > n // 4:
                return x
        return arr[0]
# @lc code=end
