#
# @lc app=leetcode id=500 lang=python3
#
# [500] Keyboard Row
#
# https://leetcode.com/problems/keyboard-row/description/
#
# algorithms
# Easy (74.22%)
# Likes:    1850
# Dislikes: 1160
# Total Accepted:    345K
# Total Submissions: 465K
# Testcase Example:  "[\"Hello\",\"Alaska\",\"Dad\",\"Peace\"]"
#
# Given an array of strings words, return the words that can be typed using
# letters of the alphabet on only one row of American keyboard like the image
# below.
#
# Note that the strings are case-insensitive, both lowercased and uppercased of
# the same letter are treated as if they are at the same row.
#
# In the American keyboard:
#
# the first row consists of the characters "qwertyuiop",
#
# the second row consists of the characters "asdfghjkl", and
#
# the third row consists of the characters "zxcvbnm".
#
# Example 1:
#
# Input: words = ["Hello","Alaska","Dad","Peace"]
#
# Output: ["Alaska","Dad"]
#
# Explanation:
#
# Both "a" and "A" are in the 2nd row of the American keyboard due to case
# insensitivity.
#
# Example 2:
#
# Input: words = ["omk"]
#
# Output: []
#
# Example 3:
#
# Input: words = ["adsdf","sfd"]
#
# Output: ["adsdf","sfd"]
#
# Constraints:
#
# 1 <= words.length <= 20
#
# 1 <= words[i].length <= 100
#
# words[i] consists of English letters (both lowercase and uppercase).
#

# @lc code=start
from typing import List


class Solution:
    def findWords(self, words: List[str]) -> List[str]:
        """
        Interview explanation:
        Words typable with letters from a single keyboard row. Map each letter
        to its row; accept word if all letters share one row.

        Algorithm:
        - rows = ["qwertyuiop","asdfghjkl","zxcvbnm"]; letter→row id.
        - Keep word if set of row ids for its letters has size 1.

        Complexity: O(total letters) time, O(1) extra space.
        """
        row_of = {}
        for i, row in enumerate(["qwertyuiop", "asdfghjkl", "zxcvbnm"]):
            for ch in row:
                row_of[ch] = i
        ans = []
        for w in words:
            rows = {row_of[c] for c in w.lower()}
            if len(rows) == 1:
                ans.append(w)
        return ans
# @lc code=end
