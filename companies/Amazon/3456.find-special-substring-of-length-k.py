#
# @lc app=leetcode id=3456 lang=python3
#
# [3456] Find Special Substring of Length K
#
# https://leetcode.com/problems/find-special-substring-of-length-k/description/
#
# algorithms
# Easy (35.29%)
# Likes:    67
# Dislikes: 10
# Total Accepted:    43.2K
# Total Submissions: 122.5K
# Testcase Example:  "\"aaabaaa\"\n3"
#
#
# You are given a string s and an integer k.
#
# Determine if there exists a substring of length exactly k in s that
# satisfies the following conditions:
#
# The substring consists of only one distinct character (e.g., "aaa" or
# "bbb").
#
# If there is a character immediately before the substring, it must be
# different from the character in the substring.
#
# If there is a character immediately after the substring, it must also be
# different from the character in the substring.
#
# Return true if such a substring exists. Otherwise, return false.
#
# Example 1:
#
# Input: s = "aaabaaa", k = 3
#
# Output: true
#
# Explanation:
#
# The substring s[4..6] == "aaa" satisfies the conditions.
#
# It has a length of 3.
#
# All characters are the same.
#
# The character before "aaa" is 'b', which is different from 'a'.
#
# There is no character after "aaa".
#
# Example 2:
#
# Input: s = "abc", k = 2
#
# Output: false
#
# Explanation:
#
# There is no substring of length 2 that consists of one distinct
# character and satisfies the conditions.
#
# Constraints:
#
# 1 <= k <= s.length <= 100
#
# s consists of lowercase English letters only.
#

# @lc code=start

class Solution:
    def hasSpecialSubstring(self, s: str, k: int) -> bool:
        """
        Interview explanation:
        Need a run of exactly k identical letters (bounded by different chars or ends).

        Algorithm:
        - Scan run lengths; return True if any run length equals k.

        Complexity: O(n) time, O(1) space.

        Alternate: check every window s[i:i+k] all equal and boundary chars differ.
        """
        n = len(s)
        i = 0
        while i < n:
            j = i
            while j < n and s[j] == s[i]:
                j += 1
            if j - i == k:
                return True
            i = j
        return False
# @lc code=end
