#
# @lc app=leetcode id=264 lang=python3
#
# [264] Ugly Number II
#
# https://leetcode.com/problems/ugly-number-ii/description/
#
# algorithms
# Medium (49.74%)
# Likes:    6921
# Dislikes: 456
# Total Accepted:    553K
# Total Submissions: 1.1M
# Testcase Example:  "10"
#
# An ugly number is a positive integer whose prime factors are limited to 2, 3,
# and 5.
#
# Given an integer n, return the n^th ugly number.
#
# Example 1:
#
# Input: n = 10
# Output: 12
# Explanation: [1, 2, 3, 4, 5, 6, 8, 9, 10, 12] is the sequence of the first 10
# ugly numbers.
#
# Example 2:
#
# Input: n = 1
# Output: 1
# Explanation: 1 has no prime factors, therefore all of its prime factors are
# limited to 2, 3, and 5.
#
# Constraints:
#
# 1 <= n <= 1690
#

# @lc code=start
class Solution:
    def nthUglyNumber(self, n: int) -> int:
        """
        Interview explanation:
        DP with three pointers: every ugly number is a previous one times 2, 3,
        or 5. Advance the pointer(s) that produced the next minimum.

        Algorithm:
        - ugly[0] = 1; i2 = i3 = i5 = 0.
        - For i in 1..n-1: next = min(ugly[i2]*2, ugly[i3]*3, ugly[i5]*5).
        - Advance each pointer whose product equals next.

        Complexity: O(n) time, O(n) space.
        """
        ugly = [0] * n
        ugly[0] = 1
        i2 = i3 = i5 = 0
        for i in range(1, n):
            n2, n3, n5 = ugly[i2] * 2, ugly[i3] * 3, ugly[i5] * 5
            nxt = min(n2, n3, n5)
            ugly[i] = nxt
            if nxt == n2:
                i2 += 1
            if nxt == n3:
                i3 += 1
            if nxt == n5:
                i5 += 1
        return ugly[-1]
# @lc code=end
