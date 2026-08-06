#
# @lc app=leetcode id=3340 lang=python3
#
# [3340] Check Balanced String
#
# https://leetcode.com/problems/check-balanced-string/description/
#
# algorithms
# Easy (83.05%)
# Likes:    150
# Dislikes: 3
# Total Accepted:    84.2K
# Total Submissions: 101.4K
# Testcase Example:  "\"1234\""
#
#
# You are given a string num consisting of only digits. A string of digits
# is called balanced if the sum of the digits at even indices is equal to
# the sum of digits at odd indices.
#
# Return true if num is balanced, otherwise return false.
#
# Example 1:
#
# Input: num = "1234"
#
# Output: false
#
# Explanation:
#
# The sum of digits at even indices is 1 + 3 == 4, and the sum of digits
# at odd indices is 2 + 4 == 6.
#
# Since 4 is not equal to 6, num is not balanced.
#
# Example 2:
#
# Input: num = "24123"
#
# Output: true
#
# Explanation:
#
# The sum of digits at even indices is 2 + 1 + 3 == 6, and the sum of
# digits at odd indices is 4 + 2 == 6.
#
# Since both are equal the num is balanced.
#
# Constraints:
#
# 2 <= num.length <= 100
#
# num consists of digits only
#

# @lc code=start

class Solution:
    def isBalanced(self, num: str) -> bool:
        """
        Interview explanation:
        Balanced iff sum of digits at even indices equals sum at odd indices.

        Algorithm:
        - Single pass accumulating (+even, -odd) or two running sums.
        - Alternate: sum(num[::2]) == sum(num[1::2]) with int casts.

        Complexity: O(n) time, O(1) space.
        """
        even = odd = 0
        for i, ch in enumerate(num):
            if i & 1:
                odd += ord(ch) - 48
            else:
                even += ord(ch) - 48
        return even == odd
# @lc code=end

