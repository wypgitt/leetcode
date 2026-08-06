#
# @lc app=leetcode id=65 lang=python3
#
# [65] Valid Number
#
# https://leetcode.com/problems/valid-number/description/
#
# algorithms
# Hard (23.38%)
# Likes:    1523
# Dislikes: 2220
# Total Accepted:    540K
# Total Submissions: 2.3M
# Testcase Example:  "\"0\""
#
# Given a string s, return whether s is a valid number.
#
# For example, all the following are valid numbers: "2", "0089", "-0.1",
# "+3.14", "4.", "-.9", "2e10", "-90E3", "3e+7", "+6e-1", "53.5e93",
# "-123.456e789", while the following are not valid numbers: "abc", "1a", "1e",
# "e3", "99e2.5", "--6", "-+3", "95a54e53".
#
# Formally, a valid number is defined using one of the following definitions:
#
# An integer number followed by an optional exponent.
#
# A decimal number followed by an optional exponent.
#
# An integer number is defined with an optional sign '-' or '+' followed by
# digits.
#
# A decimal number is defined with an optional sign '-' or '+' followed by one
# of the following definitions:
#
# Digits followed by a dot '.'.
#
# Digits followed by a dot '.' followed by digits.
#
# A dot '.' followed by digits.
#
# An exponent is defined with an exponent notation 'e' or 'E' followed by an
# integer number.
#
# The digits are defined as one or more digits.
#
# Example 1:
#
# Input: s = "0"
#
# Output: true
#
# Example 2:
#
# Input: s = "e"
#
# Output: false
#
# Example 3:
#
# Input: s = "."
#
# Output: false
#
# Constraints:
#
# 1 <= s.length <= 20
#
# s consists of only English letters (both uppercase and lowercase), digits
# (0-9), plus '+', minus '-', or dot '.'.
#

# @lc code=start
class Solution:
    def isNumber(self, s: str) -> bool:
        """
        Interview explanation:
        A valid number is an optional sign, a decimal or integer, and an
        optional exponent ('e'/'E' + optional sign + integer). Track what has
        been seen while scanning once (careful parse / light DFA).

        Algorithm:
        - Scan each char; maintain seen_digit, seen_dot, seen_exp.
        - Signs only allowed at start or right after e/E.
        - Dot only before exponent and at most once.
        - Exponent requires a prior digit and is followed by an integer.
        - Must end having seen a digit (and after exp, a digit after exp).

        Complexity: O(n) time, O(1) space.
        """
        return self.isNumber_parse(s)

    def isNumber_parse(self, s: str) -> bool:
        """
        Interview explanation:
        Single-pass careful parse with boolean flags (same as primary).

        Algorithm:
        - Enforce sign/dot/exponent/digit rules while scanning.

        Complexity: O(n) time, O(1) space.
        """
        seen_digit = seen_dot = seen_exp = False

        for i, ch in enumerate(s):
            if ch.isdigit():
                seen_digit = True
            elif ch in "+-":
                if i > 0 and s[i - 1] not in "eE":
                    return False
            elif ch == ".":
                if seen_dot or seen_exp:
                    return False
                seen_dot = True
            elif ch in "eE":
                if seen_exp or not seen_digit:
                    return False
                seen_exp = True
                seen_digit = False
            else:
                return False

        return seen_digit

    def isNumber_dfa(self, s: str) -> bool:
        """
        Interview explanation:
        Explicit DFA over states for optional sign, integer/fraction parts,
        and optional exponent. Accepting states require a completed number.

        Algorithm:
        - States encode progress through number grammar; reject on invalid
          transitions; accept only in digit-bearing terminal states.

        Complexity: O(n) time, O(1) space.
        """
        # 0 start, 1 sign, 2 digit, 3 dot after digit, 4 dot before digit,
        # 5 digit after dot, 6 exp, 7 exp sign, 8 exp digit
        transition = {
            0: {"sign": 1, "digit": 2, "dot": 4},
            1: {"digit": 2, "dot": 4},
            2: {"digit": 2, "dot": 3, "exp": 6},
            3: {"digit": 5, "exp": 6},
            4: {"digit": 5},
            5: {"digit": 5, "exp": 6},
            6: {"sign": 7, "digit": 8},
            7: {"digit": 8},
            8: {"digit": 8},
        }
        accept = {2, 3, 5, 8}
        state = 0

        for ch in s:
            if ch in "+-":
                key = "sign"
            elif ch.isdigit():
                key = "digit"
            elif ch == ".":
                key = "dot"
            elif ch in "eE":
                key = "exp"
            else:
                return False
            if key not in transition[state]:
                return False
            state = transition[state][key]

        return state in accept
# @lc code=end
