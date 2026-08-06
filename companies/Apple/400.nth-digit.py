#
# @lc app=leetcode id=400 lang=python3
#
# [400] Nth Digit
#
# https://leetcode.com/problems/nth-digit/description/
#
# algorithms
# Medium (38.7%)
# Likes:    1270
# Dislikes: 2166
# Total Accepted:    142K
# Total Submissions: 367K
# Testcase Example:  "3"
#
# Given an integer n, return the n^th digit of the infinite integer sequence
# [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, ...].
#
# Example 1:
#
# Input: n = 3
# Output: 3
#
# Example 2:
#
# Input: n = 11
# Output: 0
# Explanation: The 11^th digit of the sequence 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
# 11, ... is a 0, which is part of the number 10.
#
# Constraints:
#
# 1 <= n <= 2^31 - 1
#

# @lc code=start
class Solution:
    def findNthDigit(self, n: int) -> int:
        """
        Interview explanation:
        Digits are concatenated 1234567891011.... Count digit blocks by length:
        1-digit: 9 nums * 1, 2-digit: 90 * 2, 3-digit: 900 * 3, ... Skip whole
        blocks until n falls inside a length-d block, then find the number and
        digit.

        Algorithm:
        - length, count, start = 1, 9, 1
        - While n > length*count: n -= length*count; length++; count*=10; start*=10
        - number = start + (n-1)//length; digit = str(number)[(n-1)%length]

        Complexity: O(log n) time, O(1) space.
        """
        length = 1
        count = 9
        start = 1
        while n > length * count:
            n -= length * count
            length += 1
            count *= 10
            start *= 10
        num = start + (n - 1) // length
        return int(str(num)[(n - 1) % length])
# @lc code=end
