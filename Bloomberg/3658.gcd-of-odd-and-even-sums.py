#
# @lc app=leetcode id=3658 lang=python3
#
# [3658] GCD of Odd and Even Sums
#
# https://leetcode.com/problems/gcd-of-odd-and-even-sums/description/
#
# algorithms
# Easy (89.85%)
# Likes:    377
# Dislikes: 75
# Total Accepted:    290.1K
# Total Submissions: 322.8K
# Testcase Example:  "4"
#
#
# You are given an integer n. Your task is to compute the GCD (greatest
# common divisor) of two values:
#
# sumOdd: the sum of the smallest n positive odd numbers.
#
# sumEven: the sum of the smallest n positive even numbers.
#
# Return the GCD of sumOdd and sumEven.
#
# Example 1:
#
# Input: n = 4
#
# Output: 4
#
# Explanation:
#
# Sum of the first 4 odd numbers sumOdd = 1 + 3 + 5 + 7 = 16
#
# Sum of the first 4 even numbers sumEven = 2 + 4 + 6 + 8 = 20
#
# Hence, GCD(sumOdd, sumEven) = GCD(16, 20) = 4.
#
# Example 2:
#
# Input: n = 5
#
# Output: 5
#
# Explanation:
#
# Sum of the first 5 odd numbers sumOdd = 1 + 3 + 5 + 7 + 9 = 25
#
# Sum of the first 5 even numbers sumEven = 2 + 4 + 6 + 8 + 10 = 30
#
# Hence, GCD(sumOdd, sumEven) = GCD(25, 30) = 5.
#
# Constraints:
#
# 1 <= n <= 10​​​​​​​00
#

# @lc code=start
import math


class Solution:
    def gcdOfOddEvenSums(self, n: int) -> int:
        """
        Interview explanation:
        First n odds sum to n²; first n evens sum to n(n+1); gcd is n.

        Algorithm:
        - Return n (equivalently math.gcd(n*n, n*(n+1))).

        Complexity: O(1).
        """
        return n

    def gcdOfOddEvenSums_explicit(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: compute both closed forms and call gcd.

        Algorithm:
        - math.gcd(n*n, n*(n+1)).

        Complexity: O(log n).
        """
        return math.gcd(n * n, n * (n + 1))
# @lc code=end

