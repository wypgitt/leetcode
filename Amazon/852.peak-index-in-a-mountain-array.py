#
# @lc app=leetcode id=852 lang=python3
#
# [852] Peak Index in a Mountain Array
#
# https://leetcode.com/problems/peak-index-in-a-mountain-array/description/
#
# algorithms
# Medium (66.73%)
# Likes:    8623
# Dislikes: 1954
# Total Accepted:    1.3M
# Total Submissions: 1.9M
# Testcase Example:  "[0,1,0]"
#
# You are given an integer mountain array arr of length n where the values
# increase to a peak element and then decrease.
#
# Return the index of the peak element.
#
# Your task is to solve it in O(log(n)) time complexity.
#
# Example 1:
#
# Input: arr = [0,1,0]
#
# Output: 1
#
# Example 2:
#
# Input: arr = [0,2,1,0]
#
# Output: 1
#
# Example 3:
#
# Input: arr = [0,10,5,2]
#
# Output: 1
#
# Constraints:
#
# 3 <= arr.length <= 10^5
#
# 0 <= arr[i] <= 10^6
#
# arr is guaranteed to be a mountain array.
#

# @lc code=start

from typing import List


class Solution:
    def peakIndexInMountainArray(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Mountain array: strictly increases then decreases. Binary search for the
        unique peak where arr[mid] > arr[mid+1] means peak is at mid or left.

        Algorithm (binary search):
        - lo,hi; while lo<hi: mid=(lo+hi)//2; if arr[mid]<arr[mid+1]: lo=mid+1
          else hi=mid. Return lo.

        Complexity: O(log n) time, O(1) space.
        """
        lo, hi = 0, len(arr) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if arr[mid] < arr[mid + 1]:
                lo = mid + 1
            else:
                hi = mid
        return lo

    def peakIndexInMountainArray_linear(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Linear scan: peak is the index of the maximum element (unique in mountain).

        Algorithm:
        - Return argmax(arr) via one pass or builtin.

        Complexity: O(n) time, O(1) space.
        """
        return max(range(len(arr)), key=lambda i: arr[i])
# @lc code=end
