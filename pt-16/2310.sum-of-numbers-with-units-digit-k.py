#
# @lc app=leetcode id=2310 lang=python3
#
# [2310] Sum of Numbers With Units Digit K
#
# https://leetcode.com/problems/sum-of-numbers-with-units-digit-k/description/
#
# algorithms
# Medium (28.43%)
# Likes:    439
# Dislikes: 339
# Total Accepted:    33.5K
# Total Submissions: 117.9K
# Testcase Example:  "58\n9"
#
# Given two integers num and k, consider a set of positive integers with the
# following properties:
#
#
# The units digit of each integer is k.
#
#
# The sum of the integers is num.
#
# Return the minimum possible size of such a set, or -1 if no such set exists.
#
# Note:
#
#
# The set can contain multiple instances of the same integer, and the sum of an
# empty set is considered 0.
#
#
# The units digit of a number is the rightmost digit of the number.
#
#
#
# Example 1:
#
# Input: num = 58, k = 9
# Output: 2
# Explanation:
# One valid set is [9,49], as the sum is 58 and each integer has a units digit
# of 9.
# Another valid set is [19,39].
# It can be shown that 2 is the minimum possible size of a valid set.
#
# Example 2:
#
# Input: num = 37, k = 2
# Output: -1
# Explanation: It is not possible to obtain a sum of 37 using only integers that
# have a units digit of 2.
#
# Example 3:
#
# Input: num = 0, k = 7
# Output: 0
# Explanation: The sum of an empty set is considered 0.
#
#
#
# Constraints:
#
#
# 0 <= num <= 3000
#
#
# 0 <= k <= 9
#

# @lc code=start
class Solution:
    def minimumNumbers(self, num: int, k: int) -> int:
        """
        Interview explanation:
        Find minimum count of positive integers each with units digit k that
        sum to num; return -1 if impossible.

        Algorithm:
        - Try size i = 1..min(num,10): need i*k ≡ num (mod 10) and i*k <= num.
        - Special case num==0 -> 0.

        Complexity: O(1) time, O(1) space.
        """
        if num == 0:
            return 0
        for i in range(1, min(num, 10) + 1):
            if i * k <= num and (i * k) % 10 == num % 10:
                return i
        return -1

    def minimumNumbers_math(self, num: int, k: int) -> int:
        """
        Interview explanation:
        Math/modular alternate of the same check.

        Algorithm:
        - Enumerate residue-feasible counts up to 10.

        Complexity: O(1) time, O(1) space.
        """
        return self.minimumNumbers(num, k)
# @lc code=end
