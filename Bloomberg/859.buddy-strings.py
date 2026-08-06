#
# @lc app=leetcode id=859 lang=python3
#
# [859] Buddy Strings
#
# https://leetcode.com/problems/buddy-strings/description/
#
# algorithms
# Easy (34.15%)
# Likes:    3379
# Dislikes: 1848
# Total Accepted:    301K
# Total Submissions: 881K
# Testcase Example:  "\"ab\""
#
# Given two strings s and goal, return true if you can swap two letters in s so
# the result is equal to goal, otherwise, return false.
#
# Swapping letters is defined as taking two indices i and j (0-indexed) such
# that i != j and swapping the characters at s[i] and s[j].
#
# For example, swapping at indices 0 and 2 in "abcd" results in "cbad".
#
# Example 1:
#
# Input: s = "ab", goal = "ba"
# Output: true
# Explanation: You can swap s[0] = 'a' and s[1] = 'b' to get "ba", which is
# equal to goal.
#
# Example 2:
#
# Input: s = "ab", goal = "ab"
# Output: false
# Explanation: The only letters you can swap are s[0] = 'a' and s[1] = 'b',
# which results in "ba" != goal.
#
# Example 3:
#
# Input: s = "aa", goal = "aa"
# Output: true
# Explanation: You can swap s[0] = 'a' and s[1] = 'a' to get "aa", which is
# equal to goal.
#
# Constraints:
#
# 1 <= s.length, goal.length <= 2 * 10^4
#
# s and goal consist of lowercase letters.
#

# @lc code=start

class Solution:
    def buddyStrings(self, s: str, goal: str) -> bool:
        """
        Interview explanation:
        Swap exactly two letters in s to equal goal. Cases: (1) s==goal and
        some letter appears ≥2 (swap duplicates); (2) exactly two mismatch
        indices that cross-swap correctly.

        Algorithm:
        - Length check; if equal: any freq≥2. Else collect diffs; check len==2
          and swap matches.

        Complexity: O(n) time, O(1) space (alphabet).
        """
        if len(s) != len(goal):
            return False
        if s == goal:
            return len(set(s)) < len(s)
        diffs = [(a, b) for a, b in zip(s, goal) if a != b]
        return len(diffs) == 2 and diffs[0] == diffs[1][::-1]
# @lc code=end
