#
# @lc app=leetcode id=2607 lang=python3
#
# [2607] Make K-Subarray Sums Equal
#
# https://leetcode.com/problems/make-k-subarray-sums-equal/description/
#
# algorithms
# Medium (38.95%)
# Likes:    532
# Dislikes: 89
# Total Accepted:    15K
# Total Submissions: 38.4K
# Testcase Example:  "[1,4,1,3]\n2"
#
# You are given a 0-indexed integer array arr and an integer k. The array arr is
# circular. In other words, the first element of the array is the next element
# of the last element, and the last element of the array is the previous element
# of the first element.
#
# You can do the following operation any number of times:
#
#
# Pick any element from arr and increase or decrease it by 1.
#
# Return the minimum number of operations such that the sum of each subarray of
# length k is equal.
#
# A subarray is a contiguous part of the array.
#
#
#
# Example 1:
#
# Input: arr = [1,4,1,3], k = 2
# Output: 1
# Explanation: we can do one operation on index 1 to make its value equal to 3.
# The array after the operation is [1,3,1,3]
# - Subarray starts at index 0 is [1, 3], and its sum is 4
# - Subarray starts at index 1 is [3, 1], and its sum is 4
# - Subarray starts at index 2 is [1, 3], and its sum is 4
# - Subarray starts at index 3 is [3, 1], and its sum is 4
#
# Example 2:
#
# Input: arr = [2,5,5,7], k = 3
# Output: 5
# Explanation: we can do three operations on index 0 to make its value equal to
# 5 and two operations on index 3 to make its value equal to 5.
# The array after the operations is [5,5,5,5]
# - Subarray starts at index 0 is [5, 5, 5], and its sum is 15
# - Subarray starts at index 1 is [5, 5, 5], and its sum is 15
# - Subarray starts at index 2 is [5, 5, 5], and its sum is 15
# - Subarray starts at index 3 is [5, 5, 5], and its sum is 15
#
#
#
# Constraints:
#
#
# 1 <= k <= arr.length <= 10^5
#
#
# 1 <= arr[i] <= 10^9
#

# @lc code=start
from typing import List
from math import gcd


class Solution:
    def makeSubKSumEqual(self, arr: List[int], k: int) -> int:
        """
        Interview explanation:
        Equal k-subarray sums on a circular array force arr[i] == arr[i+g] for
        g = gcd(k, n); minimize moves to equalize each residue class.

        Algorithm:
        - g = gcd(k, n); for each residue r in 0..g-1, collect the class,
          sort, move all elements to the median; sum absolute deviations.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(arr)
        g = gcd(k, n)
        ops = 0
        for r in range(g):
            group = sorted(arr[r::g])
            med = group[len(group) // 2]
            ops += sum(abs(x - med) for x in group)
        return ops
# @lc code=end
