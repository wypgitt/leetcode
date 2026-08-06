#
# @lc app=leetcode id=1502 lang=python3
#
# [1502] Can Make Arithmetic Progression From Sequence
#
# https://leetcode.com/problems/can-make-arithmetic-progression-from-sequence/description/
#
# algorithms
# Easy (68.71%)
# Likes:    2362
# Dislikes: 121
# Total Accepted:    363K
# Total Submissions: 529K
# Testcase Example:  "[3,5,1]"
#
# A sequence of numbers is called an arithmetic progression if the difference
# between any two consecutive elements is the same.
#
# Given an array of numbers arr, return true if the array can be rearranged to
# form an arithmetic progression. Otherwise, return false.
#
# Example 1:
#
# Input: arr = [3,5,1]
# Output: true
# Explanation: We can reorder the elements as [1,3,5] or [5,3,1] with
# differences 2 and -2 respectively, between each consecutive elements.
#
# Example 2:
#
# Input: arr = [1,2,4]
# Output: false
# Explanation: There is no way to reorder the elements to obtain an arithmetic
# progression.
#
# Constraints:
#
# 2 <= arr.length <= 1000
#
# -10^6 <= arr[i] <= 10^6
#

# @lc code=start
from typing import List


class Solution:
    def canMakeArithmeticProgression(self, arr: List[int]) -> bool:
        """
        Interview explanation:
        After sorting, an AP has constant difference between consecutive terms.
        Sort then verify every gap equals the first gap.

        Algorithm:
        - Sort arr; d = arr[1]-arr[0]; check arr[i]-arr[i-1]==d for all i.

        Complexity: O(n log n) time, O(n) or O(1) extra depending on sort.
        """
        arr.sort()
        d = arr[1] - arr[0]
        for i in range(2, len(arr)):
            if arr[i] - arr[i - 1] != d:
                return False
        return True

    def canMakeArithmeticProgression_set(self, arr: List[int]) -> bool:
        """
        Interview explanation:
        Alternate O(n) with min/max: common difference d=(max-min)/(n-1) must
        divide exactly; every min+i*d must appear once.

        Algorithm:
        - mn, mx = min/max; if (mx-mn)%(n-1)!=0 fail; set check all AP terms.

        Complexity: O(n) time, O(n) space.
        """
        n = len(arr)
        mn, mx = min(arr), max(arr)
        if mx == mn:
            return True
        if (mx - mn) % (n - 1) != 0:
            return False
        d = (mx - mn) // (n - 1)
        seen = set(arr)
        if len(seen) != n:
            return False
        for i in range(n):
            if mn + i * d not in seen:
                return False
        return True
# @lc code=end
