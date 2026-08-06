#
# @lc app=leetcode id=660 lang=python3
#
# [660] Remove 9
#
# https://leetcode.com/problems/remove-9/description/
#
# algorithms
# Hard (57.47%)
# Likes:    167
# Dislikes: 204
# Total Accepted:    11.4K
# Total Submissions: 19.8K
# Testcase Example:  "9"
#
#
# Start from integer 1, remove any integer that contains 9 such as 9, 19,
# 29...
#
# Now, you will have a new integer sequence [1, 2, 3, 4, 5, 6, 7, 8, 10,
# 11, ...].
#
# Given an integer n, return the n^th (1-indexed) integer in the new
# sequence.
#
# Example 1:
#
# Input: n = 9
# Output: 10
#
# Example 2:
#
# Input: n = 10
# Output: 11
#
# Constraints:
#
# 1 <= n <= 8 * 10^8
#
# @lc code=start

class Solution:
    def newInteger(self, n: int) -> int:
        """
        Interview explanation:
        Premium. Numbers written without digit 9 are exactly base-9 numbers
        displayed with digits 0-8. The n-th such number is n in base 9.

        Algorithm:
        - Convert n to base 9; interpret digit string as decimal.

        Complexity: O(log n) time, O(1) space.
        """
        digits = []
        while n:
            digits.append(str(n % 9))
            n //= 9
        return int("".join(reversed(digits))) if digits else 0
# @lc code=end
