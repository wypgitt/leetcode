#
# @lc app=leetcode id=2847 lang=python3
#
# [2847] Smallest Number With Given Digit Product
#
# https://leetcode.com/problems/smallest-number-with-given-digit-product/description/
#
# algorithms
# Medium (43.56%)
# Likes:    22
# Dislikes: 1
# Total Accepted:    1.5K
# Total Submissions: 3.4K
# Testcase Example:  "105"
#
#
# Given a positive integer n, return a string representing the smallest
# positive integer such that the product of its digits is equal to n, or
# "-1" if no such number exists.
#
# Example 1:
#
# Input: n = 105
# Output: "357"
# Explanation: 3 * 5 * 7 = 105. It can be shown that 357 is the smallest
# number with a product of digits equal to 105. So the answer would be
# "357".
#
# Example 2:
#
# Input: n = 7
# Output: "7"
# Explanation: Since 7 has only one digit, its product of digits would be
# 7. We will show that 7 is the smallest number with a product of digits
# equal to 7. Since the product of numbers 1 to 6 is 1 to 6 respectively,
# so "7" would be the answer.
#
# Example 3:
#
# Input: n = 44
# Output: "-1"
# Explanation: It can be shown that there is no number such that its
# product of digits is equal to 44. So the answer would be "-1".
#
# Constraints:
#
# 1 <= n <= 10^18
#
# @lc code=start
class Solution:
    def smallestNumber(self, n: int) -> str:
        """
        Interview explanation:
        Premium: given positive n, return the smallest positive integer (as a string)
        whose digits multiply to n, or "-1" if impossible.

        Algorithm:
        - Greedily factor n using digits 9..2 (fewest digits, then ascending order).
        - If a remainder > 1 remains, a prime factor > 9 exists -> "-1".
        - n == 1 -> "1".

        Complexity: O(log n) time, O(1) extra space (digits length O(log n)).
        """
        if n == 1:
            return "1"
        digits = []
        for d in range(9, 1, -1):
            while n % d == 0:
                digits.append(str(d))
                n //= d
        if n > 1:
            return "-1"
        return "".join(reversed(digits))
# @lc code=end
