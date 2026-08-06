#
# @lc app=leetcode id=1796 lang=python3
#
# [1796] Second Largest Digit in a String
#
# https://leetcode.com/problems/second-largest-digit-in-a-string/description/
#
# algorithms
# Easy (55.0%)
# Likes:    615
# Dislikes: 133
# Total Accepted:    114K
# Total Submissions: 207K
# Testcase Example:  "\"dfa12321afd\""
#
# Given an alphanumeric string s, return the second largest numerical digit
# that appears in s, or -1 if it does not exist.
#
# An alphanumeric string is a string consisting of lowercase English letters
# and digits.
#
# Example 1:
#
# Input: s = "dfa12321afd"
# Output: 2
# Explanation: The digits that appear in s are [1, 2, 3]. The second largest
# digit is 2.
#
# Example 2:
#
# Input: s = "abc1111"
# Output: -1
# Explanation: The digits that appear in s are [1]. There is no second largest
# digit.
#
# Constraints:
#
# 1 <= s.length <= 500
#
# s consists of only lowercase English letters and digits.
#

# @lc code=start
class Solution:
    def secondHighest(self, s: str) -> int:
        """
        Interview explanation:
        Among digit characters in s, return the second largest distinct digit
        or -1 if fewer than two distinct digits.

        Algorithm:
        - Track largest and second-largest distinct digit values while scanning.

        Complexity: O(n) time, O(1) space.
        """
        first = second = -1
        for ch in s:
            if ch.isdigit():
                d = ord(ch) - 48
                if d > first:
                    second = first
                    first = d
                elif second < d < first:
                    second = d
        return second

    def secondHighest_set(self, s: str) -> int:
        """
        Interview explanation:
        Alternate: collect distinct digits into a set; sort descending; pick [1].

        Algorithm:
        - digits = {int(c) for c in s if c.isdigit()}; sorted reverse; return [1] or -1.

        Complexity: O(n) time, O(1) space (≤10 digits).
        """
        digits = sorted({int(c) for c in s if c.isdigit()}, reverse=True)
        return digits[1] if len(digits) >= 2 else -1
# @lc code=end
