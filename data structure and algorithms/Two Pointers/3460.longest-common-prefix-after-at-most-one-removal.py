#
# @lc app=leetcode id=3460 lang=python3
#
# [3460] Longest Common Prefix After at Most One Removal
#
# https://leetcode.com/problems/longest-common-prefix-after-at-most-one-removal/description/
#
# algorithms
# Medium (68.53%)
# Likes:    8
# Dislikes: 1
# Total Accepted:    1.4K
# Total Submissions: 2K
# Testcase Example:  "\"madxa\"\n\"madam\""
#
#
# You are given two strings s and t.
#
# Return the length of the longest common prefix between s and t after
# removing at most one character from s.
#
# Note: s can be left without any removal.
#
# Example 1:
#
# Input: s = "madxa", t = "madam"
#
# Output: 4
#
# Explanation:
#
# Removing s[3] from s results in "mada", which has a longest common
# prefix of length 4 with t.
#
# Example 2:
#
# Input: s = "leetcode", t = "eetcode"
#
# Output: 7
#
# Explanation:
#
# Removing s[0] from s results in "eetcode", which matches t.
#
# Example 3:
#
# Input: s = "one", t = "one"
#
# Output: 3
#
# Explanation:
#
# No removal is needed.
#
# Example 4:
#
# Input: s = "a", t = "b"
#
# Output: 0
#
# Explanation:
#
# s and t cannot have a common prefix.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# 1 <= t.length <= 10^5
#
# s and t contain only lowercase English letters.
#

# @lc code=start

class Solution:
    def longestCommonPrefix(self, s: str, t: str) -> int:
        """
        Interview explanation:
        Longest prefix of t that is a subsequence of a prefix of s after deleting
        at most one character from s (equivalently: match t while skipping <=1 in s).

        Algorithm:
        - Two pointers over s,t; on mismatch, skip once in s if still allowed.

        Complexity: O(|s|+|t|) time, O(1) space.
        """
        i = j = 0
        can_skip = True
        while i < len(s) and j < len(t):
            if s[i] == t[j]:
                i += 1
                j += 1
            elif can_skip:
                i += 1
                can_skip = False
            else:
                return j
        return j
# @lc code=end
