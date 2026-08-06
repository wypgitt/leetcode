#
# @lc app=leetcode id=2710 lang=python3
#
# [2710] Remove Trailing Zeros From a String
#
# https://leetcode.com/problems/remove-trailing-zeros-from-a-string/description/
#
# algorithms
# Easy (79.87%)
# Likes:    345
# Dislikes: 13
# Total Accepted:    100.5K
# Total Submissions: 125.9K
# Testcase Example:  "\"51230100\""
#
# Given a positive integer num represented as a string, return the integer num
# without trailing zeros as a string.
#
#
#
# Example 1:
#
# Input: num = "51230100"
# Output: "512301"
# Explanation: Integer "51230100" has 2 trailing zeros, we remove them and
# return integer "512301".
#
# Example 2:
#
# Input: num = "123"
# Output: "123"
# Explanation: Integer "123" has no trailing zeros, we return integer "123".
#
#
#
# Constraints:
#
#
# 1 <= num.length <= 1000
#
#
# num consists of only digits.
#
#
# num doesn't have any leading zeros.
#

# @lc code=start
class Solution:
    def removeTrailingZeros(self, num: str) -> str:
        """
        Interview explanation:
        Strip trailing zeros from a numeric string.

        Algorithm:
        - rstrip('0').

        Complexity: O(n) time, O(n) space for the result.
        """
        return num.rstrip("0")
# @lc code=end
