#
# @lc app=leetcode id=658 lang=python3
#
# [658] Find K Closest Elements
#
# https://leetcode.com/problems/find-k-closest-elements/description/
#
# algorithms
# Medium (49.97%)
# Likes:    9187
# Dislikes: 957
# Total Accepted:    851K
# Total Submissions: 1.7M
# Testcase Example:  "[1,2,3,4,5]"
#
# Given a sorted integer array arr, two integers k and x, return the k closest
# integers to x in the array. The result should also be sorted in ascending
# order.
#
# An integer a is closer to x than an integer b if:
#
# |a - x| < |b - x|, or
#
# |a - x| == |b - x| and a < b
#
# Example 1:
#
# Input: arr = [1,2,3,4,5], k = 4, x = 3
#
# Output: [1,2,3,4]
#
# Example 2:
#
# Input: arr = [1,1,2,3,4,5], k = 4, x = -1
#
# Output: [1,1,2,3]
#
# Constraints:
#
# 1 <= k <= arr.length
#
# 1 <= arr.length <= 10^4
#
# arr is sorted in ascending order.
#
# -10^4 <= arr[i], x <= 10^4
#

# @lc code=start

from typing import List


class Solution:
    def findClosestElements(self, arr: List[int], k: int, x: int) -> List[int]:
        """
        Interview explanation:
        Sorted array: find window of size k closest to x. Binary search the left
        bound of the window in [0, n-k].

        Algorithm:
        - Binary search lo in [0, n-k]: compare x-arr[mid] vs arr[mid+k]-x.
        - If x farther from left, move lo = mid+1 else hi = mid.
        - Return arr[lo:lo+k].

        Complexity: O(log(n-k) + k) time, O(1) extra.
        """
        lo, hi = 0, len(arr) - k
        while lo < hi:
            mid = (lo + hi) // 2
            if x - arr[mid] > arr[mid + k] - x:
                lo = mid + 1
            else:
                hi = mid
        return arr[lo : lo + k]

    def findClosestElements_two_pointers(
        self, arr: List[int], k: int, x: int
    ) -> List[int]:
        """
        Interview explanation:
        Alternate classic: two pointers from both ends shrink until length k,
        always discard the farther endpoint.

        Algorithm:
        - lo, hi = 0, n-1; while hi-lo+1 > k: shrink side farther from x.

        Complexity: O(N) time, O(1) extra.
        """
        lo, hi = 0, len(arr) - 1
        while hi - lo + 1 > k:
            if abs(arr[lo] - x) > abs(arr[hi] - x):
                lo += 1
            else:
                hi -= 1
        return arr[lo : hi + 1]
# @lc code=end
