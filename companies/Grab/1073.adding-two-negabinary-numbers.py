#
# @lc app=leetcode id=1073 lang=python3
#
# [1073] Adding Two Negabinary Numbers
#
# https://leetcode.com/problems/adding-two-negabinary-numbers/description/
#
# algorithms
# Medium (38.07%)
# Likes:    341
# Dislikes: 132
# Total Accepted:    22.8K
# Total Submissions: 60.0K
# Testcase Example:  "[1,1,1,1,1]"
#
# Given two numbers arr1 and arr2 in base -2, return the result of adding them
# together.
#
# Each number is given in array format: as an array of 0s and 1s, from most
# significant bit to least significant bit. For example, arr = [1,1,0,1]
# represents the number (-2)^3 + (-2)^2 + (-2)^0 = -3. A number arr in array,
# format is also guaranteed to have no leading zeros: either arr == [0] or
# arr[0] == 1.
#
# Return the result of adding arr1 and arr2 in the same format: as an array of
# 0s and 1s with no leading zeros.
#
# Example 1:
#
# Input: arr1 = [1,1,1,1,1], arr2 = [1,0,1]
# Output: [1,0,0,0,0]
# Explanation: arr1 represents 11, arr2 represents 5, the output represents 16.
#
# Example 2:
#
# Input: arr1 = [0], arr2 = [0]
# Output: [0]
#
# Example 3:
#
# Input: arr1 = [0], arr2 = [1]
# Output: [1]
#
# Constraints:
#
# 1 <= arr1.length, arr2.length <= 1000
#
# arr1[i] and arr2[i] are 0 or 1
#
# arr1 and arr2 have no leading zeros
#

# @lc code=start
from typing import List


class Solution:
    def addNegabinary(self, arr1: List[int], arr2: List[int]) -> List[int]:
        """
        Interview explanation:
        Add base -2 from LSB. Carry rule differs from binary: when bit sum is
        2 or 3, write 0 or 1 and carry -1 (since 2 = 110 in negabinary:
        2 = (-2)^2 + (-2)^1). When sum is -1, write 1 and carry +1.

        Algorithm:
        - i,j from ends; while digits or carry: s = carry + bits; append s&1;
          carry = -(s >> 1)  (equivalently handle cases).
        - Strip leading zeros.

        Complexity: O(n + m) time, O(n + m) space.
        """
        i, j = len(arr1) - 1, len(arr2) - 1
        carry = 0
        out = []
        while i >= 0 or j >= 0 or carry:
            if i >= 0:
                carry += arr1[i]
                i -= 1
            if j >= 0:
                carry += arr2[j]
                j -= 1
            out.append(carry & 1)
            carry = -(carry >> 1)
        while len(out) > 1 and out[-1] == 0:
            out.pop()
        out.reverse()
        return out
# @lc code=end
