#
# @lc app=leetcode id=1156 lang=python3
#
# [1156] Swap For Longest Repeated Character Substring
#
# https://leetcode.com/problems/swap-for-longest-repeated-character-substring/description/
#
# algorithms
# Medium (44.83%)
# Likes:    1126
# Dislikes: 105
# Total Accepted:    43.6K
# Total Submissions: 97.2K
# Testcase Example:  "\"bbaababbba\""
#
# You are given a string text. You can swap two of the characters in the text.
#
# Return the length of the longest substring with repeated characters.
#
# Example 1:
#
# Input: text = "ababa"
# Output: 3
# Explanation: We can swap the first 'b' with the last 'a', or the last 'b'
# with the first 'a'. Then, the longest repeated character substring is "aaa"
# with length 3.
#
# Example 2:
#
# Input: text = "aaabaaa"
# Output: 6
# Explanation: Swap 'b' with the last 'a' (or the first 'a'), and we get
# longest repeated character substring "aaaaaa" with length 6.
#
# Example 3:
#
# Input: text = "aaaaa"
# Output: 5
# Explanation: No need to swap, longest repeated character substring is "aaaaa"
# with length is 5.
#
# Constraints:
#
# 1 <= text.length <= 2 * 10^4
#
# text consist of lowercase English characters only.
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def maxRepOpt1(self, text: str) -> int:
        """
        Interview explanation:
        At most one swap to maximize longest run of the same character.
        Consider groups of consecutive equal chars; can extend a group by 1
        if another occurrence exists, or merge two groups of same char separated
        by one different char if total count allows.

        Algorithm:
        - Compress into (char, length) groups.
        - For each group: min(len+1, total[ch]) if spare exists.
        - For groups i and i+2 same char with middle length 1: merge lens + maybe 1.

        Complexity: O(n) time, O(n) space for groups.
        """
        n = len(text)
        total = Counter(text)
        groups: List[List] = []
        i = 0
        while i < n:
            j = i
            while j < n and text[j] == text[i]:
                j += 1
            groups.append([text[i], j - i])
            i = j

        ans = 0
        for ch, length in groups:
            ans = max(ans, min(length + 1, total[ch]))

        for i in range(1, len(groups) - 1):
            if groups[i - 1][0] == groups[i + 1][0] and groups[i][1] == 1:
                ch = groups[i - 1][0]
                ans = max(ans, min(groups[i - 1][1] + groups[i + 1][1] + 1, total[ch]))
        return ans
# @lc code=end
