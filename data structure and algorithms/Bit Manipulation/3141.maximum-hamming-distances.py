#
# @lc app=leetcode id=3141 lang=python3
#
# [3141] Maximum Hamming Distances
#
# https://leetcode.com/problems/maximum-hamming-distances/description/
#
# algorithms
# Hard (49.67%)
# Likes:    15
# Dislikes: 2
# Total Accepted:    669
# Total Submissions: 1.3K
# Testcase Example:  "[9,12,9,11]\n4"
#
#
# Given an array nums and an integer m, with each element nums[i]
# satisfying 0 <= nums[i] < 2^m, return an array answer. The answer array
# should be of the same length as nums, where each element answer[i]
# represents the maximum Hamming distance between nums[i] and any other
# element nums[j] in the array.
#
# The Hamming distance between two binary integers is defined as the
# number of positions at which the corresponding bits differ (add leading
# zeroes if needed).
#
# Example 1:
#
# Input: nums = [9,12,9,11], m = 4
#
# Output: [2,3,2,3]
#
# Explanation:
#
# The binary representation of nums = [1001,1100,1001,1011].
#
# The maximum hamming distances for each index are:
#
# nums[0]: 1001 and 1100 have a distance of 2.
#
# nums[1]: 1100 and 1011 have a distance of 3.
#
# nums[2]: 1001 and 1100 have a distance of 2.
#
# nums[3]: 1011 and 1100 have a distance of 3.
#
# Example 2:
#
# Input: nums = [3,4,6,10], m = 4
#
# Output: [3,3,2,3]
#
# Explanation:
#
# The binary representation of nums = [0011,0100,0110,1010].
#
# The maximum hamming distances for each index are:
#
# nums[0]: 0011 and 0100 have a distance of 3.
#
# nums[1]: 0100 and 0011 have a distance of 3.
#
# nums[2]: 0110 and 1010 have a distance of 2.
#
# nums[3]: 1010 and 0100 have a distance of 3.
#
# Constraints:
#
# 1 <= m <= 17
#
# 2 <= nums.length <= 2^m
#
# 0 <= nums[i] < 2^m
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def maxHammingDistances(self, nums: List[int], m: int) -> List[int]:
        """
        Interview explanation:
        For each nums[i] in {0..2^m-1}, find max Hamming distance to any
        nums[j]. Equivalently m minus min distance from the bit-complement of
        nums[i] to the set.

        Algorithm:
        - Multi-source BFS on the m-dimensional hypercube from all values in
          nums -> dist[v] = min Hamming distance to the set.
        - answer[i] = m - dist[nums[i] XOR ((1<<m)-1)].

        Complexity: O(m * 2^m) time and space.
        """
        mask = (1 << m) - 1
        dist = [m + 1] * (1 << m)
        q: deque = deque()
        for x in set(nums):
            dist[x] = 0
            q.append(x)
        while q:
            u = q.popleft()
            for b in range(m):
                v = u ^ (1 << b)
                if dist[v] > dist[u] + 1:
                    dist[v] = dist[u] + 1
                    q.append(v)
        return [m - dist[x ^ mask] for x in nums]
# @lc code=end
