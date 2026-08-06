#
# @lc app=leetcode id=2734 lang=python3
#
# [2734] Lexicographically Smallest String After Substring Operation
#
# https://leetcode.com/problems/lexicographically-smallest-string-after-substring-operation/description/
#
# algorithms
# Medium (35.32%)
# Likes:    283
# Dislikes: 195
# Total Accepted:    37.1K
# Total Submissions: 105.1K
# Testcase Example:  "\"cbabc\""
#
# Given a string s consisting of lowercase English letters. Perform the
# following operation:
#
#
# Select any non-empty substring then replace every letter of the substring with
# the preceding letter of the English alphabet. For example, 'b' is converted to
# 'a', and 'a' is converted to 'z'.
#
# Return the lexicographically smallest string after performing the operation.
#
#
#
# Example 1:
#
# Input: s = "cbabc"
#
# Output: "baabc"
#
# Explanation:
#
# Perform the operation on the substring starting at index 0, and ending at
# index 1 inclusive.
#
# Example 2:
#
# Input: s = "aa"
#
# Output: "az"
#
# Explanation:
#
# Perform the operation on the last letter.
#
# Example 3:
#
# Input: s = "acbbc"
#
# Output: "abaab"
#
# Explanation:
#
# Perform the operation on the substring starting at index 1, and ending at
# index 4 inclusive.
#
# Example 4:
#
# Input: s = "leetcode"
#
# Output: "kddsbncd"
#
# Explanation:
#
# Perform the operation on the entire string.
#
#
#
# Constraints:
#
#
# 1 <= s.length <= 3 * 10^5
#
#
# s consists of lowercase English letters
#

# @lc code=start
class Solution:
    def smallestString(self, s: str) -> str:
        """
        Interview explanation:
        Exactly once: pick nonempty substring of non-'a' chars? Actually: decrease every
        char in one contiguous substring by 1 ('a' wraps to 'z' — but op forbids wrapping
        optimally). Perform the operation once to get lexicographically smallest string.

        Algorithm:
        - Find first non-'a'; decrease a maximal run of non-'a'. If all 'a's, change last to 'z'.

        Complexity: O(n) time, O(n) space.
        """
        chars = list(s)
        n = len(chars)
        i = 0
        while i < n and chars[i] == "a":
            i += 1
        if i == n:
            chars[-1] = "z"
            return "".join(chars)
        while i < n and chars[i] != "a":
            chars[i] = chr(ord(chars[i]) - 1)
            i += 1
        return "".join(chars)
# @lc code=end
