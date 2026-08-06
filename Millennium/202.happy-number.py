#
# @lc app=leetcode id=202 lang=python3
#
# [202] Happy Number
#
# https://leetcode.com/problems/happy-number/description/
#
# algorithms
# Easy (60.06%)
# Likes:    12103
# Dislikes: 1650
# Total Accepted:    2.4M
# Total Submissions: 4.0M
# Testcase Example:  "19"
#
# Write an algorithm to determine if a number n is happy.
#
# A happy number is a number defined by the following process:
#
# Starting with any positive integer, replace the number by the sum of the
# squares of its digits.
#
# Repeat the process until the number equals 1 (where it will stay), or it
# loops endlessly in a cycle which does not include 1.
#
# Those numbers for which this process ends in 1 are happy.
#
# Return true if n is a happy number, and false if not.
#
# Example 1:
#
# Input: n = 19
# Output: true
# Explanation:
# 1^2 + 9^2 = 82
# 8^2 + 2^2 = 68
# 6^2 + 8^2 = 100
# 1^2 + 0^2 + 0^2 = 1
#
# Example 2:
#
# Input: n = 2
# Output: false
#
# Constraints:
#
# 1 <= n <= 2^31 - 1
#

# @lc code=start
from typing import Set


class Solution:
    def isHappy(self, n: int) -> bool:
        """
        Interview explanation:
        Happy numbers eventually reach 1; unhappy ones enter a cycle. Floyd's
        cycle detection finds the cycle with O(1) space: slow advances one
        sum-of-squares step, fast two. Meeting at 1 means happy.

        Algorithm:
        - Define next(x) as sum of squares of digits of x.
        - Move slow = next(slow), fast = next(next(fast)) until they meet.
        - Return whether the meeting point is 1.

        Complexity: O(log n) per step; cycle length is bounded, so O(log n) time, O(1) space.
        """
        def next_val(x: int) -> int:
            total = 0
            while x:
                x, d = divmod(x, 10)
                total += d * d
            return total

        slow = n
        fast = next_val(n)
        while slow != fast:
            slow = next_val(slow)
            fast = next_val(next_val(fast))
        return slow == 1

    def isHappyHashSet(self, n: int) -> bool:
        """
        Interview explanation:
        Track seen numbers in a set. Reaching 1 means happy; revisiting a number
        means a cycle (unhappy).

        Algorithm:
        - While n != 1 and n not seen: add n, replace n with sum of digit squares.
        - Return n == 1.

        Complexity: O(log n) amortized time, O(log n) space for the seen set.
        """
        seen: Set[int] = set()
        while n != 1 and n not in seen:
            seen.add(n)
            total = 0
            while n:
                n, d = divmod(n, 10)
                total += d * d
            n = total
        return n == 1
# @lc code=end
