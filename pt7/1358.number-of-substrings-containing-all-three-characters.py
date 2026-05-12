#
# @lc app=leetcode id=1358 lang=python3
#
# [1358] Number of Substrings Containing All Three Characters
#
# https://leetcode.com/problems/number-of-substrings-containing-all-three-characters/description/
#
# algorithms
# Medium (73.67%)
# Likes:    4467
# Dislikes: 83
# Total Accepted:    458.2K
# Total Submissions: 621.5K
# Testcase Example:  '"abcabc"'
#
# Given a string s consisting only of characters a, b and c.
# 
# Return the number of substrings containing at least one occurrence of all
# these characters a, b and c.
# 
# 
# Example 1:
# 
# 
# Input: s = "abcabc"
# Output: 10
# Explanation: The substrings containing at least one occurrence of the
# characters a, b and c are "abc", "abca", "abcab", "abcabc", "bca", "bcab",
# "bcabc", "cab", "cabc" and "abc" (again). 
# 
# 
# Example 2:
# 
# 
# Input: s = "aaacb"
# Output: 3
# Explanation: The substrings containing at least one occurrence of the
# characters a, b and c are "aaacb", "aacb" and "acb". 
# 
# 
# Example 3:
# 
# 
# Input: s = "abc"
# Output: 1
# 
# 
# 
# Constraints:
# 
# 
# 3 <= s.length <= 5 x 10^4
# s only consists of a, b or c characters.
# 
# 
#

# @lc code=start
from __future__ import annotations


class Solution:
    def numberOfSubstrings(self, s: str) -> int:
        last_seen = {"a": -1, "b": -1, "c": -1}
        total = 0

        for right, char in enumerate(s):
            last_seen[char] = right
            total += min(last_seen.values()) + 1

        return total
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# For every ending index `right`, count how many substrings ending there contain
# all three characters. If the latest positions of a, b, and c are known, then
# every start index from 0 through the minimum latest position creates a valid
# substring.
#
# Data structure:
# A tiny dictionary stores the last seen index of each required character.
#
# Walkthrough:
# 1. Initialize last seen positions to -1, meaning not seen yet.
# 2. Scan from left to right and update the current character's last index.
# 3. Let `earliest = min(last_seen.values())`.
# 4. There are `earliest + 1` valid starts for substrings ending at `right`.
#
# Edge cases:
# - Before all three characters are seen, min is -1 and contributes 0.
# - Repeated characters only update their latest position.
# - Entire string valid: all starts up to the earliest last occurrence count.
#
# Complexity:
# - Time: O(n), one pass.
# - Space: O(1), only three stored positions.
