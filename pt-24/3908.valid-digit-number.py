#
# @lc app=leetcode id=3908 lang=python3
#
# [3908] Valid Digit Number
#
# https://leetcode.com/problems/valid-digit-number/description/
#
# algorithms
# Easy (70.69%)
# Likes:    19
# Dislikes: 0
# Total Accepted:    32.8K
# Total Submissions: 46.5K
# Testcase Example:  "101\n0"
#
#
# You are given an integer n and a digit x.
#
# A number is considered valid if:
#
# It contains at least one occurrence of digit x, and
#
# It does not start with digit x.
#
# Return true if n is valid, otherwise return false.
#
# Example 1:
#
# Input: n = 101, x = 0
#
# Output: true
#
# Explanation:
#
# The number contains digit 0 at index 1. It does not start with 0, so it
# satisfies both conditions. Thus, the answer is true​​​​​​​.
#
# Example 2:
#
# Input: n = 232, x = 2
#
# Output: false
#
# Explanation:
#
# The number starts with 2, which violates the condition. Thus, the answer
# is false.
#
# Example 3:
#
# Input: n = 5, x = 1
#
# Output: false
#
# Explanation:
#
# The number does not contain digit 1. Thus, the answer is false.
#
# Constraints:
#
# 0 <= n <= 10^5​​​​​​​
#
# 0 <= x <= 9
#

# @lc code=start
class Solution:
    def validDigit(self, n: int, x: int) -> bool:
        """
        Interview explanation:
        Valid iff digit x appears at least once and is not the leading digit.

        Algorithm:
        - Convert n to string; check s[0] != str(x) and str(x) in s.

        Complexity: O(log n) time, O(log n) space.
        """
        s = str(n)
        d = str(x)
        return s[0] != d and d in s
# @lc code=end
