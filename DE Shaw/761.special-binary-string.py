#
# @lc app=leetcode id=761 lang=python3
#
# [761] Special Binary String
#
# https://leetcode.com/problems/special-binary-string/description/
#
# algorithms
# Hard (79.42%)
# Likes:    1177
# Dislikes: 303
# Total Accepted:    102K
# Total Submissions: 128K
# Testcase Example:  "\"11011000\""
#
# Special binary strings are binary strings with the following two properties:
#
# The number of 0's is equal to the number of 1's.
#
# Every prefix of the binary string has at least as many 1's as 0's.
#
# You are given a special binary string s.
#
# A move consists of choosing two consecutive, non-empty, special substrings of
# s, and swapping them. Two strings are consecutive if the last character of
# the first string is exactly one index before the first character of the
# second string.
#
# Return the lexicographically largest resulting string possible after applying
# the mentioned operations on the string.
#
# Example 1:
#
# Input: s = "11011000"
# Output: "11100100"
# Explanation: The strings "10" [occuring at s[1]] and "1100" [at s[3]] are
# swapped.
# This is the lexicographically largest string possible after some number of
# swaps.
#
# Example 2:
#
# Input: s = "10"
# Output: "10"
#
# Constraints:
#
# 1 <= s.length <= 50
#
# s[i] is either '0' or '1'.
#
# s is a special binary string.
#


# @lc code=start
class Solution:
    def makeLargestSpecial(self, s: str) -> str:
        """
        Interview explanation:
        A special binary string is like a valid parentheses string (1↔'(', 0↔')').
        Recursively: split s into special substrings, make each largest, then
        sort those pieces descending and concatenate.

        Algorithm:
        - Scan balance; when balance returns to 0, piece = '1' + recurse(mid) + '0'
        - Sort pieces reverse lexicographically; join

        Complexity: O(n^2) time typical (recursion + sorts); O(n) space.
        """
        if not s:
            return s
        parts = []
        bal = i = 0
        for j, ch in enumerate(s):
            bal += 1 if ch == "1" else -1
            if bal == 0:
                parts.append("1" + self.makeLargestSpecial(s[i + 1 : j]) + "0")
                i = j + 1
        parts.sort(reverse=True)
        return "".join(parts)
# @lc code=end

