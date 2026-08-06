#
# @lc app=leetcode id=477 lang=python3
#
# [477] Total Hamming Distance
#
# https://leetcode.com/problems/total-hamming-distance/description/
#
# algorithms
# Medium (55.23%)
# Likes:    2315
# Dislikes: 97
# Total Accepted:    141K
# Total Submissions: 255K
# Testcase Example:  "[4,14,2]"
#
# The Hamming distance between two integers is the number of positions at which
# the corresponding bits are different.
#
# Given an integer array nums, return the sum of Hamming distances between all
# the pairs of the integers in nums.
#
# Example 1:
#
# Input: nums = [4,14,2]
# Output: 6
# Explanation: In binary representation, the 4 is 0100, 14 is 1110, and 2 is
# 0010 (just
# showing the four bits relevant in this case).
# The answer will be:
# HammingDistance(4, 14) + HammingDistance(4, 2) + HammingDistance(14, 2) = 2 +
# 2 + 2 = 6.
#
# Example 2:
#
# Input: nums = [4,14,4]
# Output: 4
#
# Constraints:
#
# 1 <= nums.length <= 10^4
#
# 0 <= nums[i] <= 10^9
#
# The answer for the given input will fit in a 32-bit integer.
#

# @lc code=start
from typing import List


class Solution:
    def totalHammingDistance(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Total Hamming distance = sum over bit positions of (#ones * #zeros)
        for that bit — each differing pair contributes 1 at that bit.

        Algorithm:
        - For bit b in 0..31: ones = count of nums with bit set; add
          ones * (n - ones).

        Complexity: O(32 n) = O(n) time, O(1) space.
        """
        n = len(nums)
        total = 0
        for b in range(32):
            ones = sum((x >> b) & 1 for x in nums)
            total += ones * (n - ones)
        return total
# @lc code=end
