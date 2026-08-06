#
# @lc app=leetcode id=3309 lang=python3
#
# [3309] Maximum Possible Number by Binary Concatenation
#
# https://leetcode.com/problems/maximum-possible-number-by-binary-concatenation/description/
#
# algorithms
# Medium (65.72%)
# Likes:    118
# Dislikes: 7
# Total Accepted:    38K
# Total Submissions: 57.8K
# Testcase Example:  "[1,2,3]"
#
#
# You are given an array of integers nums of size 3.
#
# Return the maximum possible number whose binary representation can be
# formed by concatenating the binary representation of all elements in
# nums in some order.
#
# Note that the binary representation of any number does not contain
# leading zeros.
#
# Example 1:
#
# Input: nums = [1,2,3]
#
# Output: 30
#
# Explanation:
#
# Concatenate the numbers in the order [3, 1, 2] to get the result
# "11110", which is the binary representation of 30.
#
# Example 2:
#
# Input: nums = [2,8,16]
#
# Output: 1296
#
# Explanation:
#
# Concatenate the numbers in the order [2, 8, 16] to get the result
# "10100010000", which is the binary representation of 1296.
#
# Constraints:
#
# nums.length == 3
#
# 1 <= nums[i] <= 127
#

# @lc code=start
from functools import cmp_to_key
from itertools import permutations
from typing import List


class Solution:
    def maxGoodNumber(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Only three numbers: try every concatenation order of their binary forms
        and take the maximum integer value.

        Algorithm:
        - For each permutation, join bin(x)[2:] and parse as base-2.

        Complexity: O(1) time (3! = 6), O(1) space.
        """
        best = 0
        for p in permutations(nums):
            s = "".join(bin(x)[2:] for x in p)
            best = max(best, int(s, 2))
        return best

    def maxGoodNumber_cmp(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Classic largest-number comparator on binary strings (a+b vs b+a).

        Algorithm:
        - Sort bins so a+b > b+a; concatenate and parse.

        Complexity: O(1) time, O(1) space.
        """
        bins = [bin(x)[2:] for x in nums]
        bins.sort(key=cmp_to_key(lambda a, b: (a + b < b + a) - (a + b > b + a)))
        return int("".join(bins), 2)
# @lc code=end
