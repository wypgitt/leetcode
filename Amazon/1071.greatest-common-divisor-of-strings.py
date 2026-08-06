#
# @lc app=leetcode id=1071 lang=python3
#
# [1071] Greatest Common Divisor of Strings
#
# https://leetcode.com/problems/greatest-common-divisor-of-strings/description/
#
# algorithms
# Easy (54.22%)
# Likes:    6087
# Dislikes: 1668
# Total Accepted:    1000K
# Total Submissions: 1.8M
# Testcase Example:  "\"ABCABC\""
#
# For two strings s and t, we say "t divides s" if and only if s = t + t + t +
# ... + t + t (i.e., t is concatenated with itself one or more times).
#
# Given two strings str1 and str2, return the largest string x such that x
# divides both str1 and str2.
#
# Example 1:
#
# Input: str1 = "ABCABC", str2 = "ABC"
#
# Output: "ABC"
#
# Example 2:
#
# Input: str1 = "ABABAB", str2 = "ABAB"
#
# Output: "AB"
#
# Example 3:
#
# Input: str1 = "LEET", str2 = "CODE"
#
# Output: ""
#
# Example 4:
#
# Input: str1 = "AAAAAB", str2 = "AAA"
#
# Output: ""
#
# Constraints:
#
# 1 <= str1.length, str2.length <= 1000
#
# str1 and str2 consist of English uppercase letters.
#

# @lc code=start
import math


class Solution:
    def gcdOfStrings(self, str1: str, str2: str) -> str:
        """
        Interview explanation:
        If a common divisor string exists, str1+str2 must equal str2+str1
        (same infinite periodic pattern). The candidate length is gcd(|s1|,|s2|);
        verify by checking both are multiples of that prefix.

        Algorithm (math + check):
        - If str1+str2 != str2+str1: return "".
        - g = gcd(len(str1), len(str2)); return str1[:g].

        Complexity: O(n + m) time, O(n + m) space for concatenations.
        """
        if str1 + str2 != str2 + str1:
            return ""
        g = math.gcd(len(str1), len(str2))
        return str1[:g]

    def gcdOfStrings_brute(self, str1: str, str2: str) -> str:
        """
        Interview explanation:
        Alternate: try prefixes of the shorter string from longest to shortest;
        a prefix of length d works only if d divides both lengths and both
        strings are that prefix repeated.

        Algorithm:
        - For L from min(n,m) down to 1: if L|n and L|m and str1==prefix*(n/L)
          and str2==prefix*(m/L): return prefix.

        Complexity: O(min(n,m)·(n+m)) time, O(n+m) space.
        """
        n, m = len(str1), len(str2)
        for L in range(min(n, m), 0, -1):
            if n % L or m % L:
                continue
            prefix = str1[:L]
            if prefix * (n // L) == str1 and prefix * (m // L) == str2:
                return prefix
        return ""
# @lc code=end
