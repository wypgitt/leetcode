#
# @lc app=leetcode id=89 lang=python3
#
# [89] Gray Code
#
# https://leetcode.com/problems/gray-code/description/
#
# algorithms
# Medium (64.81%)
# Likes:    2550
# Dislikes: 2839
# Total Accepted:    425.8K
# Total Submissions: 656.9K
# Testcase Example:  '2'
#
# An n-bit gray code sequence is a sequence of 2^n integers where:
# 
# 
# Every integer is in the inclusive range [0, 2^n - 1],
# The first integer is 0,
# An integer appears no more than once in the sequence,
# The binary representation of every pair of adjacent integers differs by
# exactly one bit, and
# The binary representation of the first and last integers differs by exactly
# one bit.
# 
# 
# Given an integer n, return any valid n-bit gray code sequence.
# 
# 
# Example 1:
# 
# 
# Input: n = 2
# Output: [0,1,3,2]
# Explanation:
# The binary representation of [0,1,3,2] is [00,01,11,10].
# - 00 and 01 differ by one bit
# - 01 and 11 differ by one bit
# - 11 and 10 differ by one bit
# - 10 and 00 differ by one bit
# [0,2,3,1] is also a valid gray code sequence, whose binary representation is
# [00,10,11,01].
# - 00 and 10 differ by one bit
# - 10 and 11 differ by one bit
# - 11 and 01 differ by one bit
# - 01 and 00 differ by one bit
# 
# 
# Example 2:
# 
# 
# Input: n = 1
# Output: [0,1]
# 
# 
# 
# Constraints:
# 
# 
# 1 <= n <= 16
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def grayCode(self, n: int) -> List[int]:
        """
        Interview explanation:
        The binary-reflected Gray code for integer i is i ^ (i >> 1). Adjacent
        integers differ in a way that this transform changes exactly one bit,
        producing the required sequence from 0 to 2^n - 1.

        Edge cases and tests:
        - n=1 returns [0, 1].
        - Sequence length is 2^n.
        - Adjacent elements, including last/first if considered cyclic, differ
          by one bit.

        Complexity: O(2^n) time for the output, O(1) extra space excluding it.
        """
        return [i ^ (i >> 1) for i in range(1 << n)]
# @lc code=end


