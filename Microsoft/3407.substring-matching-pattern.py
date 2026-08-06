#
# @lc app=leetcode id=3407 lang=python3
#
# [3407] Substring Matching Pattern
#
# https://leetcode.com/problems/substring-matching-pattern/description/
#
# algorithms
# Easy (29.19%)
# Likes:    126
# Dislikes: 52
# Total Accepted:    41K
# Total Submissions: 140.3K
# Testcase Example:  "\"leetcode\"\n\"ee*e\""
#
#
# You are given a string s and a pattern string p, where p contains
# exactly one '*' character.
#
# The '*' in p can be replaced with any sequence of zero or more
# characters.
#
# Return true if p can be made a substring of s, and false otherwise.
#
# Example 1:
#
# Input: s = "leetcode", p = "ee*e"
#
# Output: true
#
# Explanation:
#
# By replacing the '*' with "tcod", the substring "eetcode" matches the
# pattern.
#
# Example 2:
#
# Input: s = "car", p = "c*v"
#
# Output: false
#
# Explanation:
#
# There is no substring matching the pattern.
#
# Example 3:
#
# Input: s = "luck", p = "u*"
#
# Output: true
#
# Explanation:
#
# The substrings "u", "uc", and "uck" match the pattern.
#
# Constraints:
#
# 1 <= s.length <= 50
#
# 1 <= p.length <= 50
#
# s contains only lowercase English letters.
#
# p contains only lowercase English letters and exactly one '*'
#

# @lc code=start
class Solution:
    def hasMatch(self, s: str, p: str) -> bool:
        """
        Interview explanation:
        Pattern p has exactly one '*', which matches any (possibly empty)
        string. p matches as a substring iff some substring of s is
        prefix + anything + suffix.

        Algorithm:
        - Split p on '*' into left, right.
        - Find left in s; then find right in s starting after left's end.

        Complexity: O(|s|*|p|) time, O(1) extra space.
        """
        left, right = p.split("*", 1)
        i = s.find(left)
        if i < 0:
            return False
        return s.find(right, i + len(left)) >= 0
# @lc code=end
