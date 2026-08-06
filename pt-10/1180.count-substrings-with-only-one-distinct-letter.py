#
# @lc app=leetcode id=1180 lang=python3
#
# [1180] Count Substrings with Only One Distinct Letter
#
# https://leetcode.com/problems/count-substrings-with-only-one-distinct-letter/description/
#
# algorithms
# Easy (80.91%)
# Likes:    363
# Dislikes: 52
# Total Accepted:    31.7K
# Total Submissions: 39.2K
# Testcase Example:  "\"aaaba\""
#
#
# Given a string s, return the number of substrings that have only one
# distinct letter.
#
# Example 1:
#
# Input: s = "aaaba"
# Output: 8
# Explanation: The substrings with one distinct letter are "aaa", "aa",
# "a", "b".
# "aaa" occurs 1 time.
# "aa" occurs 2 times.
# "a" occurs 4 times.
# "b" occurs 1 time.
# So the answer is 1 + 2 + 4 + 1 = 8.
#
# Example 2:
#
# Input: s = "aaaaaaaaaa"
# Output: 55
#
# Constraints:
#
# 1 <= s.length <= 1000
#
# s[i] consists of only lowercase English letters.
#
# @lc code=start

class Solution:
    def countLetters(self, s: str) -> int:
        """
        Interview explanation:
        Premium: count substrings using only one distinct letter. Within a run
        of length L of the same char, there are L*(L+1)/2 such substrings.
        Sum over all runs.

        Algorithm (group runs):
        - Walk runs of equal chars; for length L add L*(L+1)//2.

        Complexity: O(n) time, O(1) space.
        """
        n = len(s)
        ans = 0
        i = 0
        while i < n:
            j = i
            while j < n and s[j] == s[i]:
                j += 1
            L = j - i
            ans += L * (L + 1) // 2
            i = j
        return ans
# @lc code=end
