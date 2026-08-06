#
# @lc app=leetcode id=3760 lang=python3
#
# [3760] Maximum Substrings With Distinct Start
#
# https://leetcode.com/problems/maximum-substrings-with-distinct-start/description/
#
# algorithms
# Medium (91.46%)
# Likes:    94
# Dislikes: 17
# Total Accepted:    68K
# Total Submissions: 74.3K
# Testcase Example:  "\"abab\""
#
#
# You are given a string s consisting of lowercase English letters.
#
# Return an integer denoting the maximum number of substrings you can
# split s into such that each substring starts with a distinct character
# (i.e., no two substrings start with the same character).
#
# Example 1:
#
# Input: s = "abab"
#
# Output: 2
#
# Explanation:
#
# Split "abab" into "a" and "bab".
#
# Each substring starts with a distinct character i.e 'a' and 'b'. Thus,
# the answer is 2.
#
# Example 2:
#
# Input: s = "abcd"
#
# Output: 4
#
# Explanation:
#
# Split "abcd" into "a", "b", "c", and "d".
#
# Each substring starts with a distinct character. Thus, the answer is 4.
#
# Example 3:
#
# Input: s = "aaaa"
#
# Output: 1
#
# Explanation:
#
# All characters in "aaaa" are 'a'.
#
# Only one substring can start with 'a'. Thus, the answer is 1.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists of lowercase English letters.
#

# @lc code=start
class Solution:
    def maxDistinct(self, s: str) -> int:
        """
        Interview explanation:
        Contiguous split where substring start characters are all distinct. Each
        distinct letter can start at most one piece, and the first occurrence of
        each letter can always open a new piece — so the maximum is |unique(s)|.

        Algorithm:
        - Return the number of distinct characters in s.

        Complexity: O(n) time, O(1) space (26 letters).
        """
        return len(set(s))

    def maxDistinct_greedy(self, s: str) -> int:
        """
        Interview explanation:
        Alternate: scan left to right and cut whenever the next char has not yet
        been used as a start.

        Algorithm:
        - Start a piece at index 0; when seeing an unused start char, cut before it.

        Complexity: O(n) time, O(1) space.
        """
        used = set()
        ans = 0
        for ch in s:
            if ch not in used:
                used.add(ch)
                ans += 1
        return ans
# @lc code=end
