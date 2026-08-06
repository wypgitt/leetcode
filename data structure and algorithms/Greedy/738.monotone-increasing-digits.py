#
# @lc app=leetcode id=738 lang=python3
#
# [738] Monotone Increasing Digits
#
# https://leetcode.com/problems/monotone-increasing-digits/description/
#
# algorithms
# Medium (49.58%)
# Likes:    1409
# Dislikes: 115
# Total Accepted:    69.5K
# Total Submissions: 140.1K
# Testcase Example:  '10'
#
# An integer has monotone increasing digits if and only if each pair of
# adjacent digits x and y satisfy x <= y.
# 
# Given an integer n, return the largest number that is less than or equal to n
# with monotone increasing digits.
# 
# 
# Example 1:
# 
# 
# Input: n = 10
# Output: 9
# 
# 
# Example 2:
# 
# 
# Input: n = 1234
# Output: 1234
# 
# 
# Example 3:
# 
# 
# Input: n = 332
# Output: 299
# 
# 
# 
# Constraints:
# 
# 
# 0 <= n <= 10^9
# 
# 
#

# @lc code=start
class Solution:
    def monotoneIncreasingDigits(self, n: int) -> int:
        digits = list(str(n))
        marker = len(digits)
        for i in range(len(digits) - 1, 0, -1):
            if digits[i - 1] > digits[i]:
                digits[i - 1] = str(int(digits[i - 1]) - 1)
                marker = i
        for i in range(marker, len(digits)):
            digits[i] = '9'
        return int(''.join(digits))
# @lc code=end

"""
Interview explanation:
Scan from right to left looking for a descent digits[i-1] > digits[i]. To fix it while staying as large as possible, decrement digits[i-1] and set every digit after it to 9. Scanning right-to-left handles cascades like 332 -> 299.

Data structure: mutable digit list.

Edge cases: already monotone numbers keep marker at the end and return unchanged. Leading zero after decrement is fine because int() normalizes it, e.g. 10 -> 9.

Complexity: O(d) time and O(d) space for d digits.
"""
