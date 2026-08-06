#
# @lc app=leetcode id=1056 lang=python3
#
# [1056] Confusing Number
#
# https://leetcode.com/problems/confusing-number/description/
#
# algorithms
# Easy (49.88%)
# Likes:    333
# Dislikes: 186
# Total Accepted:    58.3K
# Total Submissions: 116.8K
# Testcase Example:  "6"
#
#
# A confusing number is a number that when rotated 180 degrees becomes a
# different number with each digit valid.
#
# We can rotate digits of a number by 180 degrees to form new digits.
#
# When 0, 1, 6, 8, and 9 are rotated 180 degrees, they become 0, 1, 9, 8,
# and 6 respectively.
#
# When 2, 3, 4, 5, and 7 are rotated 180 degrees, they become invalid.
#
# Note that after rotating a number, we can ignore leading zeros.
#
# For example, after rotating 8000, we have 0008 which is considered as
# just 8.
#
# Given an integer n, return true if it is a confusing number, or false
# otherwise.
#
# Example 1:
#
# Input: n = 6
# Output: true
# Explanation: We get 9 after rotating 6, 9 is a valid number, and 9 != 6.
#
# Example 2:
#
# Input: n = 89
# Output: true
# Explanation: We get 68 after rotating 89, 68 is a valid number and 68 !=
# 89.
#
# Example 3:
#
# Input: n = 11
# Output: false
# Explanation: We get 11 after rotating 11, 11 is a valid number but the
# value remains the same, thus 11 is not a confusing number
#
# Constraints:
#
# 0 <= n <= 10^9
#
# @lc code=start
class Solution:
    def confusingNumber(self, n: int) -> bool:
        """
        Interview explanation:
        Premium. Digits that remain valid when rotated 180°: 0→0,1→1,6→9,8→8,9→6.
        Rotate the number (map digits and reverse); confusing iff rotated value
        differs from original and all digits are rotatable.

        Algorithm:
        - Map rotatable digits; if any digit invalid: False
        - Build rotated by mapping digits from right; compare != n

        Complexity: O(log n) time, O(log n) space.
        """
        rotate = {0: 0, 1: 1, 6: 9, 8: 8, 9: 6}
        orig = n
        rotated = 0
        while n:
            d = n % 10
            if d not in rotate:
                return False
            rotated = rotated * 10 + rotate[d]
            n //= 10
        return rotated != orig
# @lc code=end
