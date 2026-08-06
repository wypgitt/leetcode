#
# @lc app=leetcode id=1881 lang=python3
#
# [1881] Maximum Value after Insertion
#
# https://leetcode.com/problems/maximum-value-after-insertion/description/
#
# algorithms
# Medium (39.56%)
# Likes:    402
# Dislikes: 67
# Total Accepted:    34.9K
# Total Submissions: 88.3K
# Testcase Example:  "\"99\""
#
# You are given a very large integer n, represented as a string, and an integer
# digit x. The digits in n and the digit x are in the inclusive range [1, 9],
# and n may represent a negative number.
#
# You want to maximize n's numerical value by inserting x anywhere in the
# decimal representation of n. You cannot insert x to the left of the negative
# sign.
#
# For example, if n = 73 and x = 6, it would be best to insert it between 7 and
# 3, making n = 763.
#
# If n = -55 and x = 2, it would be best to insert it before the first 5,
# making n = -255.
#
# Return a string representing the maximum value of n after the insertion.
#
# Example 1:
#
# Input: n = "99", x = 9
# Output: "999"
# Explanation: The result is the same regardless of where you insert 9.
#
# Example 2:
#
# Input: n = "-13", x = 2
# Output: "-123"
# Explanation: You can make n one of {-213, -123, -132}, and the largest of
# those three is -123.
#
# Constraints:
#
# 1 <= n.length <= 10^5
#
# 1 <= x <= 9
#
# The digits in n are in the range [1, 9].
#
# n is a valid representation of an integer.
#
# In the case of a negative n, it will begin with '-'.
#

# @lc code=start
class Solution:
    def maxValue(self, n: str, x: int) -> str:
        """
        Interview explanation:
        Insert digit x into decimal string n (may be negative) to maximize value.
        Positive: insert before first digit < x. Negative: insert before first
        digit > x (to make magnitude smaller → algebraically larger).

        Algorithm:
        - If n[0]!='-': find first i with int(n[i])<x; insert there (or end).
        - Else: find first i>0 with int(n[i])>x; insert there (or end).

        Complexity: O(L) time, O(L) space for result string.
        """
        xch = str(x)
        if n[0] != "-":
            for i, ch in enumerate(n):
                if int(ch) < x:
                    return n[:i] + xch + n[i:]
            return n + xch
        for i in range(1, len(n)):
            if int(n[i]) > x:
                return n[:i] + xch + n[i:]
        return n + xch
# @lc code=end
