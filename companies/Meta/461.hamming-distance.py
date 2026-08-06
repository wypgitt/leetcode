#
# @lc app=leetcode id=461 lang=python3
#
# [461] Hamming Distance
#
# https://leetcode.com/problems/hamming-distance/description/
#
# algorithms
# Easy (76.98%)
# Likes:    4045
# Dislikes: 231
# Total Accepted:    708K
# Total Submissions: 920K
# Testcase Example:  "1"
#
# The Hamming distance between two integers is the number of positions at which
# the corresponding bits are different.
#
# Given two integers x and y, return the Hamming distance between them.
#
# Example 1:
#
# Input: x = 1, y = 4
# Output: 2
# Explanation:
# 1 (0 0 0 1)
# 4 (0 1 0 0)
# ↑ ↑
# The above arrows point to positions where the corresponding bits are
# different.
#
# Example 2:
#
# Input: x = 3, y = 1
# Output: 1
#
# Constraints:
#
# 0 <= x, y <= 2^31 - 1
#
# Note: This question is the same as 2220: Minimum Bit Flips to Convert Number.
#

# @lc code=start
class Solution:
    def hammingDistance(self, x: int, y: int) -> int:
        """
        Interview explanation:
        Hamming distance = number of differing bits = popcount(x XOR y).

        Algorithm:
        - return (x ^ y).bit_count()  (or Brian Kernighan loop).

        Complexity: O(1) / O(bits) time, O(1) space.
        """
        return (x ^ y).bit_count()

    def hammingDistance_kernighan(self, x: int, y: int) -> int:
        """
        Interview explanation:
        Alternate: Brian Kernighan — repeatedly clear lowest set bit of xor
        until zero; count clears.

        Algorithm:
        - z = x^y; while z: z &= z-1; cnt++.

        Complexity: O(set bits) time, O(1) space.
        """
        z = x ^ y
        cnt = 0
        while z:
            z &= z - 1
            cnt += 1
        return cnt
# @lc code=end
