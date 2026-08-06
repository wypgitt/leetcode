#
# @lc app=leetcode id=3769 lang=python3
#
# [3769] Sort Integers by Binary Reflection
#
# https://leetcode.com/problems/sort-integers-by-binary-reflection/description/
#
# algorithms
# Easy (61.26%)
# Likes:    63
# Dislikes: 6
# Total Accepted:    32K
# Total Submissions: 52.3K
# Testcase Example:  "[4,5,4]"
#
#
# You are given an integer array nums.
#
# The binary reflection of a positive integer is defined as the number
# obtained by reversing the order of its binary digits (ignoring any
# leading zeros) and interpreting the resulting binary number as a
# decimal.
#
# Sort the array in ascending order based on the binary reflection of each
# element. If two different numbers have the same binary reflection, the
# smaller original number should appear first.
#
# Return the resulting sorted array.
#
# Example 1:
#
# Input: nums = [4,5,4]
#
# Output: [4,4,5]
#
# Explanation:
#
# Binary reflections are:
#
# 4 -> (binary) 100 -> (reversed) 001 -> 1
#
# 5 -> (binary) 101 -> (reversed) 101 -> 5
#
# 4 -> (binary) 100 -> (reversed) 001 -> 1
#
# Sorting by the reflected values gives [4, 4, 5].
#
# Example 2:
#
# Input: nums = [3,6,5,8]
#
# Output: [8,3,6,5]
#
# Explanation:
#
# Binary reflections are:
#
# 3 -> (binary) 11 -> (reversed) 11 -> 3
#
# 6 -> (binary) 110 -> (reversed) 011 -> 3
#
# 5 -> (binary) 101 -> (reversed) 101 -> 5
#
# 8 -> (binary) 1000 -> (reversed) 0001 -> 1
#
# Sorting by the reflected values gives [8, 3, 6, 5].
#
# Note that 3 and 6 have the same reflection, so we arrange them in
# increasing order of original value.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 1 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def sortByReflection(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Sort by bit-reversed value (ignoring leading zeros), breaking ties by
        the original number ascending.

        Algorithm:
        - reverse(x): fold bits LSB-first into a new integer.
        - sorted(nums, key=lambda x: (reverse(x), x)).

        Complexity: O(n log n * bitlen) time, O(n) space.
        """
        def reverse(x: int) -> int:
            res = 0
            while x:
                res = (res << 1) | (x & 1)
                x >>= 1
            return res

        return sorted(nums, key=lambda x: (reverse(x), x))

    def sortByReflection_bin(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate: reverse via binary strings.

        Algorithm:
        - key = int(bin(x)[2:][::-1], 2), then original x.

        Complexity: O(n log n * bitlen) time, O(n) space.
        """
        return sorted(nums, key=lambda x: (int(bin(x)[2:][::-1], 2), x))
# @lc code=end
