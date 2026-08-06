#
# @lc app=leetcode id=2111 lang=python3
#
# [2111] Minimum Operations to Make the Array K-Increasing
#
# https://leetcode.com/problems/minimum-operations-to-make-the-array-k-increasing/description/
#
# algorithms
# Hard (40.81%)
# Likes:    733
# Dislikes: 16
# Total Accepted:    16.7K
# Total Submissions: 41K
# Testcase Example:  "[5,4,3,2,1]\n1"
#
# You are given a 0-indexed array arr consisting of n positive integers, and a
# positive integer k.
#
# The array arr is called K-increasing if arr[i-k] <= arr[i] holds for every
# index i, where k <= i <= n-1.
#
#
# For example, arr = [4, 1, 5, 2, 6, 2] is K-increasing for k = 2 because:
#
#
#
#
# arr[0] <= arr[2] (4 <= 5)
#
#
# arr[1] <= arr[3] (1 <= 2)
#
#
# arr[2] <= arr[4] (5 <= 6)
#
#
# arr[3] <= arr[5] (2 <= 2)
#
#
#
#
#
#
# However, the same arr is not K-increasing for k = 1 (because arr[0] > arr[1])
# or k = 3 (because arr[0] > arr[3]).
#
# In one operation, you can choose an index i and change arr[i] into any
# positive integer.
#
# Return the minimum number of operations required to make the array
# K-increasing for the given k.
#
#
#
# Example 1:
#
# Input: arr = [5,4,3,2,1], k = 1
# Output: 4
# Explanation:
# For k = 1, the resultant array has to be non-decreasing.
# Some of the K-increasing arrays that can be formed are [5,6,7,8,9],
# [1,1,1,1,1], [2,2,3,4,4]. All of them require 4 operations.
# It is suboptimal to change the array to, for example, [6,7,8,9,10] because it
# would take 5 operations.
# It can be shown that we cannot make the array K-increasing in less than 4
# operations.
#
# Example 2:
#
# Input: arr = [4,1,5,2,6,2], k = 2
# Output: 0
# Explanation:
# This is the same example as the one in the problem description.
# Here, for every index i where 2 <= i <= 5, arr[i-2] <= arr[i].
# Since the given array is already K-increasing, we do not need to perform any
# operations.
#
# Example 3:
#
# Input: arr = [4,1,5,2,6,2], k = 3
# Output: 2
# Explanation:
# Indices 3 and 5 are the only ones not satisfying arr[i-3] <= arr[i] for 3 <= i
# <= 5.
# One of the ways we can make the array K-increasing is by changing arr[3] to 4
# and arr[5] to 5.
# The array will now be [4,1,5,4,6,5].
# Note that there can be other ways to make the array K-increasing, but none of
# them require less than 2 operations.
#
#
#
# Constraints:
#
#
# 1 <= arr.length <= 10^5
#
#
# 1 <= arr[i], k <= arr.length
#


# @lc code=start
from typing import List
import bisect


class Solution:
    def kIncreasing(self, arr: List[int], k: int) -> int:
        """
        Interview explanation:
        Array is k-increasing if arr[i] <= arr[i+k] for all valid i. Min changes
        so this holds. Independent chains: indices i, i+k, i+2k, ...

        Algorithm:
        - For each residue class mod k, compute LIS length (non-decreasing) via
          patience sorting; operations = len(chain) - LIS.

        Complexity: O(n log(n/k)) time, O(n/k) space.
        """
        n = len(arr)
        ans = 0
        for start in range(k):
            seq = [arr[i] for i in range(start, n, k)]
            # longest non-decreasing subsequence length
            tails = []
            for x in seq:
                i = bisect.bisect_right(tails, x)
                if i == len(tails):
                    tails.append(x)
                else:
                    tails[i] = x
            ans += len(seq) - len(tails)
        return ans
# @lc code=end

