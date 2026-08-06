#
# @lc app=leetcode id=1790 lang=python3
#
# [1790] Check if One String Swap Can Make Strings Equal
#
# https://leetcode.com/problems/check-if-one-string-swap-can-make-strings-equal/description/
#
# algorithms
# Easy (49.53%)
# Likes:    1719
# Dislikes: 87
# Total Accepted:    315K
# Total Submissions: 636K
# Testcase Example:  "\"bank\""
#
# You are given two strings s1 and s2 of equal length. A string swap is an
# operation where you choose two indices in a string (not necessarily
# different) and swap the characters at these indices.
#
# Return true if it is possible to make both strings equal by performing at
# most one string swap on exactly one of the strings. Otherwise, return false.
#
# Example 1:
#
# Input: s1 = "bank", s2 = "kanb"
# Output: true
# Explanation: For example, swap the first character with the last character of
# s2 to make "bank".
#
# Example 2:
#
# Input: s1 = "attack", s2 = "defend"
# Output: false
# Explanation: It is impossible to make them equal with one string swap.
#
# Example 3:
#
# Input: s1 = "kelb", s2 = "kelb"
# Output: true
# Explanation: The two strings are already equal, so no string swap operation
# is required.
#
# Constraints:
#
# 1 <= s1.length, s2.length <= 100
#
# s1.length == s2.length
#
# s1 and s2 consist of only lowercase English letters.
#

# @lc code=start
class Solution:
    def areAlmostEqual(self, s1: str, s2: str) -> bool:
        """
        Interview explanation:
        Strings are equal after at most one swap in s1 iff they are equal, or
        they differ at exactly two indices that form a reciprocal swap.

        Algorithm:
        - Collect differing indices; 0 → True; 2 → check swap equality; else False.

        Complexity: O(n) time, O(1) space.
        """
        diff = [i for i in range(len(s1)) if s1[i] != s2[i]]
        if not diff:
            return True
        if len(diff) != 2:
            return False
        i, j = diff
        return s1[i] == s2[j] and s1[j] == s2[i]

    def areAlmostEqual_count(self, s1: str, s2: str) -> bool:
        """
        Interview explanation:
        Alternate: early-exit scan tracking up to two mismatch positions.

        Algorithm:
        - Walk once; store first two mismatch indices; reject a third; verify swap.

        Complexity: O(n).
        """
        a = b = -1
        for i, (x, y) in enumerate(zip(s1, s2)):
            if x != y:
                if a < 0:
                    a = i
                elif b < 0:
                    b = i
                else:
                    return False
        if a < 0:
            return True
        if b < 0:
            return False
        return s1[a] == s2[b] and s1[b] == s2[a]
# @lc code=end
