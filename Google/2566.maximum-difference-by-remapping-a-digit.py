#
# @lc app=leetcode id=2566 lang=python3
#
# [2566] Maximum Difference by Remapping a Digit
#
# https://leetcode.com/problems/maximum-difference-by-remapping-a-digit/description/
#
# algorithms
# Easy (75.55%)
# Likes:    617
# Dislikes: 76
# Total Accepted:    135.8K
# Total Submissions: 179.8K
# Testcase Example:  "11891"
#
# You are given an integer num. You know that Bob will sneakily remap one of the
# 10 possible digits (0 to 9) to another digit.
#
# Return the difference between the maximum and minimum values Bob can make by
# remapping exactly one digit in num.
#
# Notes:
#
#
# When Bob remaps a digit d1 to another digit d2, Bob replaces all occurrences
# of d1 in num with d2.
#
#
# Bob can remap a digit to itself, in which case num does not change.
#
#
# Bob can remap different digits for obtaining minimum and maximum values
# respectively.
#
#
# The resulting number after remapping can contain leading zeroes.
#
#
#
# Example 1:
#
# Input: num = 11891
# Output: 99009
# Explanation:
# To achieve the maximum value, Bob can remap the digit 1 to the digit 9 to
# yield 99899.
# To achieve the minimum value, Bob can remap the digit 1 to the digit 0,
# yielding 890.
# The difference between these two numbers is 99009.
#
# Example 2:
#
# Input: num = 90
# Output: 99
# Explanation:
# The maximum value that can be returned by the function is 99 (if 0 is replaced
# by 9) and the minimum value that can be returned by the function is 0 (if 9 is
# replaced by 0).
# Thus, we return 99.
#
#
#
# Constraints:
#
#
# 1 <= num <= 10^8
#

# @lc code=start
class Solution:
    def minMaxDifference(self, num: int) -> int:
        """
        Interview explanation:
        Remap one digit d->x in the decimal representation (same mapping for max and
        independently for min) to maximize a-b after remapping.

        Algorithm:
        - Max: replace the first non-9 digit with 9 throughout.
        - Min: replace the first digit with 0 throughout.

        Complexity: O(D) time, O(D) space.
        """
        s = str(num)
        # maximize
        mx = s
        for ch in s:
            if ch != '9':
                mx = s.replace(ch, '9')
                break
        # minimize
        mn = s.replace(s[0], '0')
        return int(mx) - int(mn)
# @lc code=end
