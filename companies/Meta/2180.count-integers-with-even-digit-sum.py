#
# @lc app=leetcode id=2180 lang=python3
#
# [2180] Count Integers With Even Digit Sum
#
# https://leetcode.com/problems/count-integers-with-even-digit-sum/description/
#
# algorithms
# Easy (70.73%)
# Likes:    731
# Dislikes: 44
# Total Accepted:    105.8K
# Total Submissions: 149.5K
# Testcase Example:  "4"
#
# Given a positive integer num, return the number of positive integers less than
# or equal to num whose digit sums are even.
#
# The digit sum of a positive integer is the sum of all its digits.
#
#
#
# Example 1:
#
# Input: num = 4
# Output: 2
# Explanation:
# The only integers less than or equal to 4 whose digit sums are even are 2 and
# 4.
#
# Example 2:
#
# Input: num = 30
# Output: 14
# Explanation:
# The 14 integers less than or equal to 30 whose digit sums are even are
# 2, 4, 6, 8, 11, 13, 15, 17, 19, 20, 22, 24, 26, and 28.
#
#
#
# Constraints:
#
#
# 1 <= num <= 1000
#

# @lc code=start
class Solution:
    def countEven(self, num: int) -> int:
        """
        Interview explanation:
        Count integers in [1, num] whose digits sum to an even number.

        Algorithm:
        (math)
        - Closed form: (num - (digit_sum(num) % 2)) // 2.

        Complexity: O(log num) time, O(1) space.
        """
        s = 0
        x = num
        while x:
            s += x % 10
            x //= 10
        return (num - s % 2) // 2

    def countEven_scan(self, num: int) -> int:
        """
        Interview explanation:
        Alternate: scan 1..num and test digit-sum parity.

        Algorithm:
        - For each x, sum digits; count even sums.

        Complexity: O(num log num) time, O(1) space.
        """
        def even_digit_sum(x: int) -> bool:
            s = 0
            while x:
                s += x % 10
                x //= 10
            return s % 2 == 0

        return sum(1 for x in range(1, num + 1) if even_digit_sum(x))
# @lc code=end
