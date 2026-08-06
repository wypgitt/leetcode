#
# @lc app=leetcode id=816 lang=python3
#
# [816] Ambiguous Coordinates
#
# https://leetcode.com/problems/ambiguous-coordinates/description/
#
# algorithms
# Medium (56.41%)
# Likes:    341
# Dislikes: 668
# Total Accepted:    35.1K
# Total Submissions: 62.2K
# Testcase Example:  '"(123)"'
#
# We had some 2-dimensional coordinates, like "(1, 3)" or "(2, 0.5)". Then, we
# removed all commas, decimal points, and spaces and ended up with the string
# s.
# 
# 
# For example, "(1, 3)" becomes s = "(13)" and "(2, 0.5)" becomes s =
# "(205)".
# 
# 
# Return a list of strings representing all possibilities for what our original
# coordinates could have been.
# 
# Our original representation never had extraneous zeroes, so we never started
# with numbers like "00", "0.0", "0.00", "1.0", "001", "00.01", or any other
# number that can be represented with fewer digits. Also, a decimal point
# within a number never occurs without at least one digit occurring before it,
# so we never started with numbers like ".1".
# 
# The final answer list can be returned in any order. All coordinates in the
# final answer have exactly one space between them (occurring after the
# comma.)
# 
# 
# Example 1:
# 
# 
# Input: s = "(123)"
# Output: ["(1, 2.3)","(1, 23)","(1.2, 3)","(12, 3)"]
# 
# 
# Example 2:
# 
# 
# Input: s = "(0123)"
# Output: ["(0, 1.23)","(0, 12.3)","(0, 123)","(0.1, 2.3)","(0.1, 23)","(0.12,
# 3)"]
# Explanation: 0.0, 00, 0001 or 00.01 are not allowed.
# 
# 
# Example 3:
# 
# 
# Input: s = "(00011)"
# Output: ["(0, 0.011)","(0.001, 1)"]
# 
# 
# 
# Constraints:
# 
# 
# 4 <= s.length <= 12
# s[0] == '(' and s[s.length - 1] == ')'.
# The rest of s are digits.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def ambiguousCoordinates(self, s: str) -> List[str]:
        digits = s[1:-1]

        def forms(part: str) -> List[str]:
            if len(part) == 1:
                return [part]
            ans = []
            if part[0] != '0':
                ans.append(part)
            for i in range(1, len(part)):
                left, right = part[:i], part[i:]
                if (left == '0' or not left.startswith('0')) and not right.endswith('0'):
                    ans.append(left + '.' + right)
            return ans

        ans = []
        for i in range(1, len(digits)):
            for left in forms(digits[:i]):
                for right in forms(digits[i:]):
                    ans.append(f"({left}, {right})")
        return ans
# @lc code=end

"""
Interview explanation:
Remove the outer parentheses, split the digits into x and y parts, and generate every valid decimal representation for each part. A valid number cannot have leading zeros unless it is exactly '0', and a decimal fraction cannot end with zero.

Data structure: helper lists of valid forms for each side are combined by Cartesian product.

Edge cases: single-digit parts are always valid. '0.xxx' is valid, but '00', '00.1', and '1.0' are not.

Complexity: there are O(n) split points and O(n) decimal placements per side, so O(n^3) output-construction time in the worst case, dominated by the number/length of generated strings. Space is output size.
"""
