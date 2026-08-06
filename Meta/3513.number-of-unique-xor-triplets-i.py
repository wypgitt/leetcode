#
# @lc app=leetcode id=3513 lang=python3
#
# [3513] Number of Unique XOR Triplets I
#
# https://leetcode.com/problems/number-of-unique-xor-triplets-i/description/
#
# algorithms
# Medium (57.65%)
# Likes:    262
# Dislikes: 36
# Total Accepted:    105.5K
# Total Submissions: 183K
# Testcase Example:  "[1,2]"
#
#
# You are given an integer array nums of length n, where nums is a
# permutation of the numbers in the range [1, n].
#
# A XOR triplet is defined as the XOR of three elements nums[i] XOR
# nums[j] XOR nums[k] where i <= j <= k.
#
# Return the number of unique XOR triplet values from all possible
# triplets (i, j, k).
#
# Example 1:
#
# Input: nums = [1,2]
#
# Output: 2
#
# Explanation:
#
# The possible XOR triplet values are:
#
# (0, 0, 0) → 1 XOR 1 XOR 1 = 1
#
# (0, 0, 1) → 1 XOR 1 XOR 2 = 2
#
# (0, 1, 1) → 1 XOR 2 XOR 2 = 1
#
# (1, 1, 1) → 2 XOR 2 XOR 2 = 2
#
# The unique XOR values are {1, 2}, so the output is 2.
#
# Example 2:
#
# Input: nums = [3,1,2]
#
# Output: 4
#
# Explanation:
#
# The possible XOR triplet values include:
#
# (0, 0, 0) → 3 XOR 3 XOR 3 = 3
#
# (0, 0, 1) → 3 XOR 3 XOR 1 = 1
#
# (0, 0, 2) → 3 XOR 3 XOR 2 = 2
#
# (0, 1, 2) → 3 XOR 1 XOR 2 = 0
#
# The unique XOR values are {0, 1, 2, 3}, so the output is 4.
#
# Constraints:
#
# 1 <= n == nums.length <= 10^5
#
# 1 <= nums[i] <= n
#
# nums is a permutation of integers from 1 to n.
#

# @lc code=start
from typing import List
import math


class Solution:
    def uniqueXorTriplets(self, nums: List[int]) -> int:
        """
        Interview explanation:
        nums is a permutation of 1..n. With i <= j <= k, the set of achievable
        XORs is all integers in [0, 2^{floor(log2 n)+1}) once n >= 3; for n < 3
        it is just the n distinct values themselves.

        Algorithm:
        - If n < 3: return n; else return 1 << (floor(log2 n) + 1).

        Complexity: O(1) time and space.
        """
        n = len(nums)
        if n < 3:
            return n
        return 1 << (int(math.log2(n)) + 1)
# @lc code=end
