#
# @lc app=leetcode id=1317 lang=python3
#
# [1317] Convert Integer to the Sum of Two No-Zero Integers
#
# https://leetcode.com/problems/convert-integer-to-the-sum-of-two-no-zero-integers/description/
#
# algorithms
# Easy (59.16%)
# Likes:    871
# Dislikes: 371
# Total Accepted:    213K
# Total Submissions: 360K
# Testcase Example:  "2"
#
# No-Zero integer is a positive integer that does not contain any 0 in its
# decimal representation.
#
# Given an integer n, return a list of two integers [a, b] where:
#
# a and b are No-Zero integers.
#
# a + b = n
#
# The test cases are generated so that there is at least one valid solution. If
# there are many valid solutions, you can return any of them.
#
# Example 1:
#
# Input: n = 2
# Output: [1,1]
# Explanation: Let a = 1 and b = 1.
# Both a and b are no-zero integers, and a + b = 2 = n.
#
# Example 2:
#
# Input: n = 11
# Output: [2,9]
# Explanation: Let a = 2 and b = 9.
# Both a and b are no-zero integers, and a + b = 11 = n.
# Note that there are other valid answers as [8, 3] that can be accepted.
#
# Constraints:
#
# 2 <= n <= 10^4
#

# @lc code=start
from typing import List


class Solution:
    def getNoZeroIntegers(self, n: int) -> List[int]:
        """
        Interview explanation:
        Find a,b > 0 with a+b=n and neither contains digit 0. Try a=1..n-1.

        Algorithm:
        - Helper no_zero(x); scan a until both a and n-a are no-zero.

        Complexity: O(n log n) time, O(1) space.
        """
        def ok(x: int) -> bool:
            return "0" not in str(x)

        for a in range(1, n):
            b = n - a
            if ok(a) and ok(b):
                return [a, b]
        return []
# @lc code=end

