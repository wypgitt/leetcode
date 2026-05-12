#
# @lc app=leetcode id=1238 lang=python3
#
# [1238] Circular Permutation in Binary Representation
#
# https://leetcode.com/problems/circular-permutation-in-binary-representation/description/
#
# algorithms
# Medium (72.65%)
# Likes:    441
# Dislikes: 195
# Total Accepted:    25K
# Total Submissions: 34.4K
# Testcase Example:  '2\n3'
#
# Given 2 integers n and start. Your task is return any permutation p of
# (0,1,2.....,2^n -1) such that :
# 
# 
# p[0] = start
# p[i] and p[i+1] differ by only one bit in their binary representation.
# p[0] and p[2^n -1] must also differ by only one bit in their binary
# representation.
# 
# 
# 
# Example 1:
# 
# 
# Input: n = 2, start = 3
# Output: [3,2,0,1]
# Explanation: The binary representation of the permutation is (11,10,00,01). 
# All the adjacent element differ by one bit. Another valid permutation is
# [3,1,0,2]
# 
# 
# Example 2:
# 
# 
# Input: n = 3, start = 2
# Output: [2,6,7,5,4,0,1,3]
# Explanation: The binary representation of the permutation is
# (010,110,111,101,100,000,001,011).
# 
# 
# 
# Constraints:
# 
# 
# 1 <= n <= 16
# 0 <= start < 2 ^ n
# 
#

# @lc code=start
from typing import List


class Solution:
    def circularPermutation(self, n: int, start: int) -> List[int]:
        return [start ^ i ^ (i >> 1) for i in range(1 << n)]
# @lc code=end

# Explanation
# -----------
# The sequence i ^ (i >> 1) is the standard n-bit Gray code: adjacent values
# differ by exactly one bit, and the last value also differs from the first by
# one bit. XOR every Gray-code value with start. XOR is a bijection that
# preserves bit differences, so the circular adjacency property remains true
# and the first value becomes start.
#
# This is better than backtracking because Gray code gives the whole valid
# Hamiltonian cycle directly.
#
# Edge cases: n = 1 gives two numbers; start can be any value from 0 to
# 2^n - 1; circular validity is preserved after the XOR shift.
#
# Time complexity: O(2^n).
# Space complexity: O(2^n) for the returned list.
