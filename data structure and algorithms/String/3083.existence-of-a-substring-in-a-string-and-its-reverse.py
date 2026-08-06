#
# @lc app=leetcode id=3083 lang=python3
#
# [3083] Existence of a Substring in a String and Its Reverse
#
# https://leetcode.com/problems/existence-of-a-substring-in-a-string-and-its-reverse/description/
#
# algorithms
# Easy (66.75%)
# Likes:    117
# Dislikes: 1
# Total Accepted:    58.5K
# Total Submissions: 87.6K
# Testcase Example:  "\"leetcode\""
#
#
# Given a string s, find any substring of length 2 which is also present
# in the reverse of s.
#
# Return true if such a substring exists, and false otherwise.
#
# Example 1:
#
# Input: s = "leetcode"
#
# Output: true
#
# Explanation: Substring "ee" is of length 2 which is also present in
# reverse(s) == "edocteel".
#
# Example 2:
#
# Input: s = "abcba"
#
# Output: true
#
# Explanation: All of the substrings of length 2 "ab", "bc", "cb", "ba"
# are also present in reverse(s) == "abcba".
#
# Example 3:
#
# Input: s = "abcd"
#
# Output: false
#
# Explanation: There is no substring of length 2 in s, which is also
# present in the reverse of s.
#
# Constraints:
#
# 1 <= s.length <= 100
#
# s consists only of lowercase English letters.
#

# @lc code=start
class Solution:
    def isSubstringPresent(self, s: str) -> bool:
        """
        Interview explanation:
        Need any length-2 substring of s that also appears in reverse(s).

        Algorithm:
        - Build reverse string; scan consecutive digrams of s for membership.

        Complexity: O(n^2) time (short n), O(n) space.
        """
        rev = s[::-1]
        for i in range(len(s) - 1):
            if s[i : i + 2] in rev:
                return True
        return False

    def isSubstringPresent_set(self, s: str) -> bool:
        """
        Interview explanation:
        Equivalent: some digram ab of s has reverse ba appearing as a digram of s.

        Algorithm:
        - Store all digrams of s in a set; check each digram's reverse.

        Complexity: O(n) time, O(n) space.
        """
        digrams = {s[i : i + 2] for i in range(len(s) - 1)}
        return any(d[::-1] in digrams for d in digrams)
# @lc code=end
