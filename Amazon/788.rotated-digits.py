#
# @lc app=leetcode id=788 lang=python3
#
# [788] Rotated Digits
#
# https://leetcode.com/problems/rotated-digits/description/
#
# algorithms
# Medium (64.07%)
# Likes:    986
# Dislikes: 1974
# Total Accepted:    225K
# Total Submissions: 352K
# Testcase Example:  "10"
#
# An integer x is a good if after rotating each digit individually by 180
# degrees, we get a valid number that is different from x. Each digit must be
# rotated - we cannot choose to leave it alone.
#
# A number is valid if each digit remains a digit after rotation. For example:
#
# 0, 1, and 8 rotate to themselves,
#
# 2 and 5 rotate to each other (in this case they are rotated in a different
# direction, in other words, 2 or 5 gets mirrored),
#
# 6 and 9 rotate to each other, and
#
# the rest of the numbers do not rotate to any other number and become invalid.
#
# Given an integer n, return the number of good integers in the range [1, n].
#
# Example 1:
#
# Input: n = 10
# Output: 4
# Explanation: There are four good numbers in the range [1, 10] : 2, 5, 6, 9.
# Note that 1 and 10 are not good numbers, since they remain unchanged after
# rotating.
#
# Example 2:
#
# Input: n = 1
# Output: 0
#
# Example 3:
#
# Input: n = 2
# Output: 1
#
# Constraints:
#
# 1 <= n <= 10^4
#

# @lc code=start
class Solution:
    def rotatedDigits(self, n: int) -> int:
        """
        Interview explanation:
        A number is "good" if every digit is rotatable (0,1,8,2,5,6,9) and at
        least one digit rotates to a different digit (2,5,6,9). Count goods in 1..n.

        Algorithm:
        - For each x in 1..n: check digits; invalid if 3/4/7; good if has 2/5/6/9.

        Complexity: O(n log n) time, O(1) space.
        """
        valid = set("0125689")
        diff = set("2569")
        ans = 0
        for x in range(1, n + 1):
            s = str(x)
            if all(c in valid for c in s) and any(c in diff for c in s):
                ans += 1
        return ans
# @lc code=end

