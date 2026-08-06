#
# @lc app=leetcode id=902 lang=python3
#
# [902] Numbers At Most N Given Digit Set
#
# https://leetcode.com/problems/numbers-at-most-n-given-digit-set/description/
#
# algorithms
# Hard (45.75%)
# Likes:    1498
# Dislikes: 98
# Total Accepted:    58.0K
# Total Submissions: 127K
# Testcase Example:  "[\"1\",\"3\",\"5\",\"7\"]"
#
# Given an array of digits which is sorted in non-decreasing order. You can
# write numbers using each digits[i] as many times as we want. For example, if
# digits = ['1','3','5'], we may write numbers such as '13', '551', and
# '1351315'.
#
# Return the number of positive integers that can be generated that are less
# than or equal to a given integer n.
#
# Example 1:
#
# Input: digits = ["1","3","5","7"], n = 100
# Output: 20
# Explanation:
# The 20 numbers that can be written are:
# 1, 3, 5, 7, 11, 13, 15, 17, 31, 33, 35, 37, 51, 53, 55, 57, 71, 73, 75, 77.
#
# Example 2:
#
# Input: digits = ["1","4","9"], n = 1000000000
# Output: 29523
# Explanation:
# We can write 3 one digit numbers, 9 two digit numbers, 27 three digit
# numbers,
# 81 four digit numbers, 243 five digit numbers, 729 six digit numbers,
# 2187 seven digit numbers, 6561 eight digit numbers, and 19683 nine digit
# numbers.
# In total, this is 29523 integers that can be written using the digits array.
#
# Example 3:
#
# Input: digits = ["7"], n = 8
# Output: 1
#
# Constraints:
#
# 1 <= digits.length <= 9
#
# digits[i].length == 1
#
# digits[i] is a digit from '1' to '9'.
#
# All the values in digits are unique.
#
# digits is sorted in non-decreasing order.
#
# 1 <= n <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def atMostNGivenDigitSet(self, digits: List[str], n: int) -> int:
        """
        Interview explanation:
        Count numbers formable from digit set that are <= n. Digit DP / digit
        counting: all shorter lengths free, then for same length walk prefix.

        Algorithm (digit DP style):
        - s=str(n), D=len(digits), L=len(s).
        - ans = sum D^i for i=1..L-1.
        - For each prefix position: count digits < s[i], then * D^(rest);
          if s[i] not in digits break; else continue. If full match +1.

        Complexity: O(log n * |digits|) time, O(log n) space.
        """
        s = str(n)
        D = len(digits)
        L = len(s)
        ans = sum(D ** i for i in range(1, L))
        digit_set = set(digits)
        for i, ch in enumerate(s):
            for d in digits:
                if d < ch:
                    ans += D ** (L - i - 1)
                else:
                    break
            if ch not in digit_set:
                return ans
        return ans + 1
# @lc code=end

