#
# @lc app=leetcode id=989 lang=python3
#
# [989] Add to Array-Form of Integer
#
# https://leetcode.com/problems/add-to-array-form-of-integer/description/
#
# algorithms
# Easy (45.64%)
# Likes:    3718
# Dislikes: 318
# Total Accepted:    352K
# Total Submissions: 771K
# Testcase Example:  "[1,2,0,0]"
#
# The array-form of an integer num is an array representing its digits in left
# to right order.
#
# For example, for num = 1321, the array form is [1,3,2,1].
#
# Given num, the array-form of an integer, and an integer k, return the
# array-form of the integer num + k.
#
# Example 1:
#
# Input: num = [1,2,0,0], k = 34
# Output: [1,2,3,4]
# Explanation: 1200 + 34 = 1234
#
# Example 2:
#
# Input: num = [2,7,4], k = 181
# Output: [4,5,5]
# Explanation: 274 + 181 = 455
#
# Example 3:
#
# Input: num = [2,1,5], k = 806
# Output: [1,0,2,1]
# Explanation: 215 + 806 = 1021
#
# Constraints:
#
# 1 <= num.length <= 10^4
#
# 0 <= num[i] <= 9
#
# num does not contain any leading zeros except for the zero itself.
#
# 1 <= k <= 10^4
#

# @lc code=start
from typing import List


class Solution:
    def addToArrayForm(self, num: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        Add k into the digit array from the least significant digit (right),
        propagating carry. Continue while carry/k remains after the array ends.

        Algorithm:
        - Walk i from n-1 down; while i>=0 or k>0: add digit+k, write digit%10,
          k//=10 (carry folded into k).
        - Reverse result (built from LSD) or insert at front.

        Complexity: O(max(n, log k)) time, O(max(n, log k)) space.
        """
        res: List[int] = []
        i = len(num) - 1
        while i >= 0 or k > 0:
            if i >= 0:
                k += num[i]
                i -= 1
            res.append(k % 10)
            k //= 10
        res.reverse()
        return res
# @lc code=end
