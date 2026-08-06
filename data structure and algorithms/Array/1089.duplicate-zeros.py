#
# @lc app=leetcode id=1089 lang=python3
#
# [1089] Duplicate Zeros
#
# https://leetcode.com/problems/duplicate-zeros/description/
#
# algorithms
# Easy (53.91%)
# Likes:    2880
# Dislikes: 800
# Total Accepted:    568K
# Total Submissions: 1.1M
# Testcase Example:  "[1,0,2,3,0,4,5,0]"
#
# Given a fixed-length integer array arr, duplicate each occurrence of zero,
# shifting the remaining elements to the right.
#
# Note that elements beyond the length of the original array are not written.
# Do the above modifications to the input array in place and do not return
# anything.
#
# Example 1:
#
# Input: arr = [1,0,2,3,0,4,5,0]
# Output: [1,0,0,2,3,0,0,4]
# Explanation: After calling your function, the input array is modified to:
# [1,0,0,2,3,0,0,4]
#
# Example 2:
#
# Input: arr = [1,2,3]
# Output: [1,2,3]
# Explanation: After calling your function, the input array is modified to:
# [1,2,3]
#
# Constraints:
#
# 1 <= arr.length <= 10^4
#
# 0 <= arr[i] <= 9
#

# @lc code=start
from typing import List


class Solution:
    def duplicateZeros(self, arr: List[int]) -> None:
        """
        Interview explanation:
        Duplicate each zero in-place, shifting right; truncate to original
        length. Count how many zeros fit, then write from the end backward so
        we never overwrite unread source cells.

        Algorithm (two-pass in-place):
        - Count zeros that fit in the effective write window.
        - Edge: a zero whose duplicate would fall past the end writes once.
        - Write from right: copy each value; if zero, write an extra zero.

        Complexity: O(n) time, O(1) extra space.
        """
        n = len(arr)
        dups = 0
        i = 0
        while i < n - dups:
            if arr[i] == 0:
                if i == n - dups - 1:
                    arr[n - 1] = 0
                    n -= 1
                    break
                dups += 1
            i += 1
        j = n - 1
        i = n - 1 - dups
        while i >= 0:
            if arr[i] == 0:
                arr[j] = 0
                j -= 1
                arr[j] = 0
            else:
                arr[j] = arr[i]
            j -= 1
            i -= 1
# @lc code=end
