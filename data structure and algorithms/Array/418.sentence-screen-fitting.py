#
# @lc app=leetcode id=418 lang=python3
#
# [418] Sentence Screen Fitting
#
# https://leetcode.com/problems/sentence-screen-fitting/description/
#
# algorithms
# Medium (36.42%)
# Likes:    1143
# Dislikes: 543
# Total Accepted:    107.5K
# Total Submissions: 295.2K
# Testcase Example:  "[\"hello\",\"world\"]\n2\n8"
#
#
# Given a rows x cols screen and a sentence represented as a list of
# strings, return the number of times the given sentence can be fitted on
# the screen.
#
# The order of words in the sentence must remain unchanged, and a word
# cannot be split into two lines. A single space must separate two
# consecutive words in a line.
#
# Example 1:
#
# Input: sentence = ["hello","world"], rows = 2, cols = 8
# Output: 1
# Explanation:
# hello---
# world---
# The character '-' signifies an empty space on the screen.
#
# Example 2:
#
# Input: sentence = ["a", "bcd", "e"], rows = 3, cols = 6
# Output: 2
# Explanation:
# a-bcd-
# e-a---
# bcd-e-
# The character '-' signifies an empty space on the screen.
#
# Example 3:
#
# Input: sentence = ["i","had","apple","pie"], rows = 4, cols = 5
# Output: 1
# Explanation:
# i-had
# apple
# pie-i
# had--
# The character '-' signifies an empty space on the screen.
#
# Constraints:
#
# 1 <= sentence.length <= 100
#
# 1 <= sentence[i].length <= 10
#
# sentence[i] consists of lowercase English letters.
#
# 1 <= rows, cols <= 2 * 10^4
#
# @lc code=start

from typing import List


class Solution:
    def wordsTyping(self, sentence: List[str], rows: int, cols: int) -> int:
        """
        Interview explanation:
        Count how many times the sentence fits on a rows×cols screen. Join
        words with spaces into one cyclic string s; for each row, advance a
        start index by cols, then back up if landing mid-word (must end on space).

        Algorithm:
        - s = " ".join(sentence) + " "; n=len(s).
        - start=0; for each row: start += cols; while start>0 and s[start%n]!=' ':
          start -= 1; then start += 1 (consume the space).
        - Return start // n.

        Complexity: O(rows * L) worst (L=max word length), O(n) space.
        Optimized with DP of next-start per position: O(n + rows).
        """
        s = " ".join(sentence) + " "
        n = len(s)
        start = 0
        for _ in range(rows):
            start += cols
            if s[start % n] == " ":
                start += 1
            else:
                while start > 0 and s[(start - 1) % n] != " ":
                    start -= 1
        return start // n

    def wordsTypingDP(self, sentence: List[str], rows: int, cols: int) -> int:
        """
        Interview explanation:
        Alternate: precompute for each starting word index how many words fit
        in one row and the next starting index; then simulate rows in O(rows).

        Algorithm:
        - For each i, greedily pack words into one row of width cols.
        - Simulate rows using the precomputed transitions; count wrapped sentences.

        Complexity: O(num_words * cols + rows) time roughly, O(num_words) space.
        """
        n = len(sentence)
        # dp[i] = (words_used_from_i_in_one_row, next_index)
        dp = [0] * n
        for i in range(n):
            length = -1  # no leading space for first word
            j = i
            count = 0
            while length + 1 + len(sentence[j]) <= cols:
                length += 1 + len(sentence[j])
                j = (j + 1) % n
                count += 1
            dp[i] = count
        words = 0
        idx = 0
        for _ in range(rows):
            words += dp[idx]
            idx = (idx + dp[idx]) % n
        return words // n
# @lc code=end
