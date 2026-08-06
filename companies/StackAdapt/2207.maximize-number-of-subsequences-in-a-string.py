#
# @lc app=leetcode id=2207 lang=python3
#
# [2207] Maximize Number of Subsequences in a String
#
# https://leetcode.com/problems/maximize-number-of-subsequences-in-a-string/description/
#
# algorithms
# Medium (36.20%)
# Likes:    535
# Dislikes: 37
# Total Accepted:    25.6K
# Total Submissions: 70.7K
# Testcase Example:  "\"abdcdbc\"\n\"ac\""
#
# You are given a 0-indexed string text and another 0-indexed string pattern of
# length 2, both of which consist of only lowercase English letters.
#
# You can add either pattern[0] or pattern[1] anywhere in text exactly once.
# Note that the character can be added even at the beginning or at the end of
# text.
#
# Return the maximum number of times pattern can occur as a subsequence of the
# modified text.
#
# A subsequence is a string that can be derived from another string by deleting
# some or no characters without changing the order of the remaining characters.
#
#
#
# Example 1:
#
# Input: text = "abdcdbc", pattern = "ac"
# Output: 4
# Explanation:
# If we add pattern[0] = 'a' in between text[1] and text[2], we get "abadcdbc".
# Now, the number of times "ac" occurs as a subsequence is 4.
# Some other strings which have 4 subsequences "ac" after adding a character to
# text are "aabdcdbc" and "abdacdbc".
# However, strings such as "abdcadbc", "abdccdbc", and "abdcdbcc", although
# obtainable, have only 3 subsequences "ac" and are thus suboptimal.
# It can be shown that it is not possible to get more than 4 subsequences "ac"
# by adding only one character.
#
# Example 2:
#
# Input: text = "aabb", pattern = "ab"
# Output: 6
# Explanation:
# Some of the strings which can be obtained from text and have 6 subsequences
# "ab" are "aaabb", "aaabb", and "aabbb".
#
#
#
# Constraints:
#
#
# 1 <= text.length <= 10^5
#
#
# pattern.length == 2
#
#
# text and pattern consist only of lowercase English letters.
#

# @lc code=start
class Solution:
    def maximumSubsequenceCount(self, text: str, pattern: str) -> int:
        """
        Interview explanation:
        After inserting pattern[0] or pattern[1] once into text, maximize the
        number of subsequences equal to the length-2 pattern.

        Algorithm:
        - If pattern[0]==pattern[1]: C(cnt+1, 2) after adding one.
        - Else base subsequence count + max(count of pattern[0], count of
          pattern[1]) from inserting at start/end respectively.

        Complexity: O(n) time, O(1) space.
        """
        a, b = pattern[0], pattern[1]
        if a == b:
            c = text.count(a)
            return c * (c + 1) // 2
        cnt_a = cnt_b = base = 0
        for ch in text:
            if ch == b:
                base += cnt_a
                cnt_b += 1
            if ch == a:
                cnt_a += 1
        return base + max(cnt_a, cnt_b)
# @lc code=end
