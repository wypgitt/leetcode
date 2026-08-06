#
# @lc app=leetcode id=2652 lang=python3
#
# [2652] Sum Multiples
#
# https://leetcode.com/problems/sum-multiples/description/
#
# algorithms
# Easy (86.32%)
# Likes:    604
# Dislikes: 45
# Total Accepted:    216.5K
# Total Submissions: 250.8K
# Testcase Example:  "7"
#
# Given a positive integer n, find the sum of all integers in the range [1, n]
# inclusive that are divisible by 3, 5, or 7.
#
# Return an integer denoting the sum of all numbers in the given range
# satisfying the constraint.
#
#
#
# Example 1:
#
# Input: n = 7
# Output: 21
# Explanation: Numbers in the range [1, 7] that are divisible by 3, 5, or 7 are
# 3, 5, 6, 7. The sum of these numbers is 21.
#
# Example 2:
#
# Input: n = 10
# Output: 40
# Explanation: Numbers in the range [1, 10] that are divisible by 3, 5, or 7 are
# 3, 5, 6, 7, 9, 10. The sum of these numbers is 40.
#
# Example 3:
#
# Input: n = 9
# Output: 30
# Explanation: Numbers in the range [1, 9] that are divisible by 3, 5, or 7 are
# 3, 5, 6, 7, 9. The sum of these numbers is 30.
#
#
#
# Constraints:
#
#
# 1 <= n <= 10^3
#

# @lc code=start

class Solution:
    def sumOfMultiples(self, n: int) -> int:
        """
        Interview explanation:
        Sum all integers in [1, n] divisible by 3, 5, or 7.

        Algorithm:
        - Inclusion-exclusion: sum multiples of 3 + 5 + 7 - 15 - 21 - 35 + 105.

        Complexity: O(1) time, O(1) space.
        """
        def s(d: int) -> int:
            m = n // d
            return d * m * (m + 1) // 2

        return s(3) + s(5) + s(7) - s(15) - s(21) - s(35) + s(105)

    def sumOfMultiples_loop(self, n: int) -> int:
        """
        Interview explanation:
        Alternate loop: scan 1..n and add multiples.

        Algorithm:
        - For each i, if i % 3/5/7 == 0 add i.

        Complexity: O(n) time, O(1) space.
        """
        return sum(i for i in range(1, n + 1) if i % 3 == 0 or i % 5 == 0 or i % 7 == 0)
# @lc code=end
