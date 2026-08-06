#
# @lc app=leetcode id=1002 lang=python3
#
# [1002] Find Common Characters
#
# https://leetcode.com/problems/find-common-characters/description/
#
# algorithms
# Easy (74.79%)
# Likes:    4555
# Dislikes: 440
# Total Accepted:    443K
# Total Submissions: 592K
# Testcase Example:  "[\"bella\",\"label\",\"roller\"]"
#
# Given a string array words, return an array of all characters that show up in
# all strings within the words (including duplicates). You may return the
# answer in any order.
#
# Example 1:
#
# Input: words = ["bella","label","roller"]
# Output: ["e","l","l"]
#
# Example 2:
#
# Input: words = ["cool","lock","cook"]
# Output: ["c","o"]
#
# Constraints:
#
# 1 <= words.length <= 100
#
# 1 <= words[i].length <= 100
#
# words[i] consists of lowercase English letters.
#

# @lc code=start
from collections import Counter
from typing import List


class Solution:
    def commonChars(self, words: List[str]) -> List[str]:
        """
        Interview explanation:
        A character appears in the answer as many times as the minimum frequency
        across all words. Intersect Counter of each word (element-wise min).

        Algorithm:
        - Start with Counter(words[0])
        - For each other word: cnt &= Counter(word) (min counts)
        - Expand cnt.elements() into a list

        Complexity: O(N * L) time where L is word length, O(1) alphabet space.
        """
        cnt = Counter(words[0])
        for w in words[1:]:
            cnt &= Counter(w)
        return list(cnt.elements())

    def commonChars_array(self, words: List[str]) -> List[str]:
        """
        Interview explanation:
        Alternate classic: maintain a size-26 min-frequency array; for each word
        count letters then take element-wise min.

        Algorithm:
        - freq[26] = inf; for each word update with its counts
        - Emit letters by remaining freq

        Complexity: O(N * L) time, O(1) space.
        """
        freq = [float("inf")] * 26
        for w in words:
            cur = [0] * 26
            for ch in w:
                cur[ord(ch) - 97] += 1
            for i in range(26):
                freq[i] = min(freq[i], cur[i])
        ans = []
        for i, f in enumerate(freq):
            ans.extend([chr(i + 97)] * int(f))
        return ans
# @lc code=end
