#
# @lc app=leetcode id=717 lang=python3
#
# [717] 1-bit and 2-bit Characters
#
# https://leetcode.com/problems/1-bit-and-2-bit-characters/description/
#
# algorithms
# Easy (49.67%)
# Likes:    1261
# Dislikes: 2362
# Total Accepted:    277K
# Total Submissions: 559K
# Testcase Example:  "[1,0,0]"
#
# We have two special characters:
#
# The first character can be represented by one bit 0.
#
# The second character can be represented by two bits (10 or 11).
#
# Given a binary array bits that ends with 0, return true if the last character
# must be a one-bit character.
#
# Example 1:
#
# Input: bits = [1,0,0]
# Output: true
# Explanation: The only way to decode it is two-bit character and one-bit
# character.
# So the last character is one-bit character.
#
# Example 2:
#
# Input: bits = [1,1,1,0]
# Output: false
# Explanation: The only way to decode it is two-bit character and two-bit
# character.
# So the last character is not one-bit character.
#
# Constraints:
#
# 1 <= bits.length <= 1000
#
# bits[i] is either 0 or 1.
#

# @lc code=start
from typing import List


class Solution:
    def isOneBitCharacter(self, bits: List[int]) -> bool:
        """
        Interview explanation:
        Decode bits as 0 or 10/11. Check whether the final 0 is a lone 1-bit
        character. Scan: skip two on 1, one on 0; succeed if we stop on last index.

        Algorithm:
        - i = 0; while i < n-1: i += 2 if bits[i] else 1; return i == n-1.

        Complexity: O(n) time, O(1) space.
        """
        i, n = 0, len(bits)
        while i < n - 1:
            i += 2 if bits[i] == 1 else 1
        return i == n - 1
# @lc code=end
