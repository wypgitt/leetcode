#
# @lc app=leetcode id=786 lang=python3
#
# [786] K-th Smallest Prime Fraction
#
# https://leetcode.com/problems/k-th-smallest-prime-fraction/description/
#
# algorithms
# Medium (69.02%)
# Likes:    2144
# Dislikes: 121
# Total Accepted:    173.2K
# Total Submissions: 250.9K
# Testcase Example:  '[1,2,3,5]\n3'
#
# You are given a sorted integer array arr containing 1 and prime numbers,
# where all the integers of arr are unique. You are also given an integer k.
# 
# For every i and j where 0 <= i < j < arr.length, we consider the fraction
# arr[i] / arr[j].
# 
# Return the k^th smallest fraction considered. Return your answer as an array
# of integers of size 2, where answer[0] == arr[i] and answer[1] == arr[j].
# 
# 
# Example 1:
# 
# 
# Input: arr = [1,2,3,5], k = 3
# Output: [2,5]
# Explanation: The fractions to be considered in sorted order are:
# 1/5, 1/3, 2/5, 1/2, 3/5, and 2/3.
# The third fraction is 2/5.
# 
# 
# Example 2:
# 
# 
# Input: arr = [1,7], k = 1
# Output: [1,7]
# 
# 
# 
# Constraints:
# 
# 
# 2 <= arr.length <= 1000
# 1 <= arr[i] <= 3 * 10^4
# arr[0] == 1
# arr[i] is a prime number for i > 0.
# All the numbers of arr are unique and sorted in strictly increasing
# order.
# 1 <= k <= arr.length * (arr.length - 1) / 2
# 
# 
# 
# Follow up: Can you solve the problem with better than O(n^2) complexity?
#

# @lc code=start
import heapq
from typing import List


class Solution:
    def kthSmallestPrimeFraction(self, arr: List[int], k: int) -> List[int]:
        n = len(arr)
        heap = [(arr[0] / arr[j], 0, j) for j in range(1, n)]
        heapq.heapify(heap)
        for _ in range(k - 1):
            _, i, j = heapq.heappop(heap)
            if i + 1 < j:
                heapq.heappush(heap, (arr[i + 1] / arr[j], i + 1, j))
        _, i, j = heapq.heappop(heap)
        return [arr[i], arr[j]]
# @lc code=end

"""
Interview explanation:
For each denominator arr[j], fractions arr[0]/arr[j], arr[1]/arr[j], ... are increasing because arr is sorted. Initialize a heap with the smallest fraction for every denominator, then pop the global smallest k times and advance within that denominator's list.

Data structure: a min-heap merges n-1 sorted fraction lists.

Edge cases: only fractions with numerator index < denominator index are pushed. k=1 returns the first heap pop.

Complexity: heap size is O(n). Each pop/push costs O(log n), so time is O((n+k) log n) and space is O(n). A binary-search counting solution can reduce dependence on k.
"""
