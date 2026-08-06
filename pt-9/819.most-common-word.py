#
# @lc app=leetcode id=819 lang=python3
#
# [819] Most Common Word
#
# https://leetcode.com/problems/most-common-word/description/
#
# algorithms
# Easy (45.29%)
# Likes:    1875
# Dislikes: 3120
# Total Accepted:    464K
# Total Submissions: 1.0M
# Testcase Example:  "\"Bob hit a ball, the hit BALL flew far after it was hit.\""
#
# Given a string paragraph and a string array of the banned words banned,
# return the most frequent word that is not banned. It is guaranteed there is
# at least one word that is not banned, and that the answer is unique.
#
# The words in paragraph are case-insensitive and the answer should be returned
# in lowercase.
#
# Note that words can not contain punctuation symbols.
#
# Example 1:
#
# Input: paragraph = "Bob hit a ball, the hit BALL flew far after it was hit.",
# banned = ["hit"]
# Output: "ball"
# Explanation:
# "hit" occurs 3 times, but it is a banned word.
# "ball" occurs twice (and no other word does), so it is the most frequent
# non-banned word in the paragraph.
# Note that words in the paragraph are not case sensitive,
# that punctuation is ignored (even if adjacent to words, such as "ball,"),
# and that "hit" isn't the answer even though it occurs more because it is
# banned.
#
# Example 2:
#
# Input: paragraph = "a.", banned = []
# Output: "a"
#
# Constraints:
#
# 1 <= paragraph.length <= 1000
#
# paragraph consists of English letters, space ' ', or one of the symbols:
# "!?',;.".
#
# 0 <= banned.length <= 100
#
# 1 <= banned[i].length <= 10
#
# banned[i] consists of only lowercase English letters.
#

# @lc code=start

from typing import List
from collections import Counter
import re


class Solution:
    def mostCommonWord(self, paragraph: str, banned: List[str]) -> str:
        """
        Interview explanation:
        Normalize to lowercase words (letters only), ignore banned set, return
        the most frequent remaining word.

        Algorithm:
        - Replace non-letters with space; split; Counter; skip banned; max by count.

        Complexity: O(n) time, O(n) space.
        """
        ban = set(banned)
        words = re.findall(r"[a-z]+", paragraph.lower())
        cnt = Counter(w for w in words if w not in ban)
        return cnt.most_common(1)[0][0]

    def mostCommonWord_manual(self, paragraph: str, banned: List[str]) -> str:
        """
        Interview explanation:
        Manual scan building words without regex — same frequency counting.

        Algorithm:
        - Walk chars; accumulate alphabetic runs; Counter; pick max not banned.

        Complexity: O(n) time, O(n) space.
        """
        ban = set(banned)
        cnt: Counter[str] = Counter()
        i, n = 0, len(paragraph)
        while i < n:
            if paragraph[i].isalpha():
                j = i
                while j < n and paragraph[j].isalpha():
                    j += 1
                w = paragraph[i:j].lower()
                if w not in ban:
                    cnt[w] += 1
                i = j
            else:
                i += 1
        return max(cnt, key=cnt.get)
# @lc code=end
