#
# @lc app=leetcode id=2165 lang=python3
#
# [2165] Smallest Value of the Rearranged Number
#
# https://leetcode.com/problems/smallest-value-of-the-rearranged-number/description/
#
# algorithms
# Medium (53.55%)
# Likes:    688
# Dislikes: 28
# Total Accepted:    50K
# Total Submissions: 93.3K
# Testcase Example:  "310"
#
# You are given an integer num. Rearrange the digits of num such that its value
# is minimized and it does not contain any leading zeros.
#
# Return the rearranged number with minimal value.
#
# Note that the sign of the number does not change after rearranging the digits.
#
#
#
# Example 1:
#
# Input: num = 310
# Output: 103
# Explanation: The possible arrangements for the digits of 310 are 013, 031,
# 103, 130, 301, 310.
# The arrangement with the smallest value that does not contain any leading
# zeros is 103.
#
# Example 2:
#
# Input: num = -7605
# Output: -7650
# Explanation: Some possible arrangements for the digits of -7605 are -7650,
# -6705, -5076, -0567.
# The arrangement with the smallest value that does not contain any leading
# zeros is -7650.
#
#
#
# Constraints:
#
#
# -10^15 <= num <= 10^15
#

# @lc code=start
class Solution:
    def smallestNumber(self, num: int) -> int:
        """
        Interview explanation:
        Rearrange digits of num to form the smallest possible integer value
        (no leading zeros except for zero itself). Negative numbers: rearrange
        digits for largest magnitude (most negative).

        Algorithm:
        - If num >= 0: sort digits ascending; move first non-zero to front.
        - If num < 0: sort digits of abs descending; negate.

        Complexity: O(d log d) for d digits, O(d) space.
        """
        if num == 0:
            return 0
        neg = num < 0
        digits = sorted(str(abs(num)), reverse=neg)
        if not neg:
            if digits[0] == "0":
                for i, c in enumerate(digits):
                    if c != "0":
                        digits[0], digits[i] = digits[i], digits[0]
                        break
        val = int("".join(digits))
        return -val if neg else val
# @lc code=end
