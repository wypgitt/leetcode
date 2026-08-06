#
# @lc app=leetcode id=467 lang=python3
#
# [467] Unique Substrings in Wraparound String
#
# https://leetcode.com/problems/unique-substrings-in-wraparound-string/description/
#
# algorithms
# Medium (43.03%)
# Likes:    1531
# Dislikes: 191
# Total Accepted:    57.1K
# Total Submissions: 132.8K
# Testcase Example:  '"a"'
#
# We define the string base to be the infinite wraparound string of
# "abcdefghijklmnopqrstuvwxyz", so base will look like this:
# 
# 
# "...zabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcd....".
# 
# 
# Given a string s, return the number of unique non-empty substrings of s are
# present in base.
# 
# 
# Example 1:
# 
# 
# Input: s = "a"
# Output: 1
# Explanation: Only the substring "a" of s is in base.
# 
# 
# Example 2:
# 
# 
# Input: s = "cac"
# Output: 2
# Explanation: There are two substrings ("a", "c") of s in base.
# 
# 
# Example 3:
# 
# 
# Input: s = "zab"
# Output: 6
# Explanation: There are six substrings ("z", "a", "b", "za", "ab", and "zab")
# of s in base.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= s.length <= 10^5
# s consists of lowercase English letters.
# 
# 
#

# @lc code=start
class Solution:
    def findSubstringInWraproundString(self, s: str) -> int:
        best = [0] * 26
        run = 0
        prev = ''
        for ch in s:
            if prev and (ord(ch) - ord(prev)) % 26 == 1:
                run += 1
            else:
                run = 1
            idx = ord(ch) - ord('a')
            best[idx] = max(best[idx], run)
            prev = ch
        return sum(best)
# @lc code=end

"""
Interview explanation:
For every ending character, only the longest valid wraparound run ending there matters. If the longest run ending at 'c' has length L, it contributes exactly L distinct substrings ending at 'c' with lengths 1..L; shorter runs are duplicates already covered.

Data structure: a 26-element array stores the maximum run length per ending character.

Edge cases: the transition from 'z' to 'a' is valid, handled by modulo 26. Repeated/non-consecutive characters reset the run to 1.

Complexity: O(n) time and O(1) space because the alphabet size is fixed.
"""
