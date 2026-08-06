#
# @lc app=leetcode id=1064 lang=python3
#
# [1064] Fixed Point
#
# https://leetcode.com/problems/fixed-point/description/
#
# algorithms
# Easy (64.33%)
# Likes:    450
# Dislikes: 67
# Total Accepted:    52.2K
# Total Submissions: 81.2K
# Testcase Example:  "[-10,-5,0,3,7]"
#
#
# Given an array of distinct integers arr, where arr is sorted in
# ascending order, return the smallest index i that satisfies arr[i] == i.
# If there is no such index, return -1.
#
# Example 1:
#
# Input: arr = [-10,-5,0,3,7]
# Output: 3
# Explanation: For the given array, arr[0] = -10, arr[1] = -5, arr[2] = 0,
# arr[3] = 3, thus the output is 3.
#
# Example 2:
#
# Input: arr = [0,2,5,8,17]
# Output: 0
# Explanation: arr[0] = 0, thus the output is 0.
#
# Example 3:
#
# Input: arr = [-10,-5,3,4,7,9]
# Output: -1
# Explanation: There is no such i that arr[i] == i, thus the output is -1.
#
# Constraints:
#
# 1 <= arr.length < 10^4
#
# -10^9 <= arr[i] <= 10^9
#
# Follow up: The O(n) solution is very straightforward. Can we do better?
#
# @lc code=start
from typing import List


class Solution:
    def fixedPoint(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Premium. Sorted distinct integers; find smallest i with arr[i]==i
        (or -1). Binary search: if arr[mid] < mid, answer is to the right;
        else go left (still may equal).

        Algorithm:
        - lo,hi=0,n-1; ans=-1
        - While lo<=hi: mid; if arr[mid]==mid: ans=mid; hi=mid-1
          elif arr[mid]<mid: lo=mid+1 else hi=mid-1

        Complexity: O(log n) time, O(1) space.
        """
        lo, hi = 0, len(arr) - 1
        ans = -1
        while lo <= hi:
            mid = (lo + hi) // 2
            if arr[mid] == mid:
                ans = mid
                hi = mid - 1
            elif arr[mid] < mid:
                lo = mid + 1
            else:
                hi = mid - 1
        return ans

    def fixedPoint_linear(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Alternate linear scan for the smallest fixed point.

        Algorithm:
        - For i,v in enumerate(arr): if i==v return i; return -1

        Complexity: O(n) time, O(1) space.
        """
        for i, v in enumerate(arr):
            if i == v:
                return i
        return -1
# @lc code=end
