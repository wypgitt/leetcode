#
# @lc app=leetcode id=941 lang=python3
#
# [941] Valid Mountain Array
#
# https://leetcode.com/problems/valid-mountain-array/description/
#
# algorithms
# Easy (35.6%)
# Likes:    3194
# Dislikes: 211
# Total Accepted:    584K
# Total Submissions: 1.6M
# Testcase Example:  "[2,1]"
#
# Given an array of integers arr, return true if and only if it is a valid
# mountain array.
#
# Recall that arr is a mountain array if and only if:
#
# arr.length >= 3
#
# There exists some i with 0 < i < arr.length - 1 such that:
#
# arr[0] < arr[1] < ... < arr[i - 1] < arr[i]
#
# arr[i] > arr[i + 1] > ... > arr[arr.length - 1]
#
# Example 1:
#
# Input: arr = [2,1]
# Output: false
#
# Example 2:
#
# Input: arr = [3,5,5]
# Output: false
#
# Example 3:
#
# Input: arr = [0,3,2,1]
# Output: true
#
# Constraints:
#
# 1 <= arr.length <= 10^4
#
# 0 <= arr[i] <= 10^4
#

# @lc code=start
from typing import List


class Solution:
    def validMountainArray(self, arr: List[int]) -> bool:
        """
        Interview explanation:
        Strictly increase to a peak then strictly decrease. Walk up while
        rising, then walk down; peak cannot be endpoints; must finish at end.

        Algorithm (two pointers / linear scan):
        - i=0; while i+1<n and arr[i]<arr[i+1]: i++
        - if i==0 or i==n-1: False
        - while i+1<n and arr[i]>arr[i+1]: i++
        - return i==n-1

        Complexity: O(n) time, O(1) space.
        """
        n = len(arr)
        i = 0
        while i + 1 < n and arr[i] < arr[i + 1]:
            i += 1
        if i == 0 or i == n - 1:
            return False
        while i + 1 < n and arr[i] > arr[i + 1]:
            i += 1
        return i == n - 1
# @lc code=end

