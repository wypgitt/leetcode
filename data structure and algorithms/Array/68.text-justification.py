#
# @lc app=leetcode id=68 lang=python3
#
# [68] Text Justification
#
# https://leetcode.com/problems/text-justification/description/
#
# algorithms
# Hard (51.79%)
# Likes:    4630
# Dislikes: 5444
# Total Accepted:    681K
# Total Submissions: 1.3M
# Testcase Example:  "[\"This\", \"is\", \"an\", \"example\", \"of\", \"text\", \"justification.\"]"
#
# Given an array of strings words and a width maxWidth, format the text such
# that each line has exactly maxWidth characters and is fully (left and right)
# justified.
#
# You should pack your words in a greedy approach; that is, pack as many words
# as you can in each line. Pad extra spaces ' ' when necessary so that each
# line has exactly maxWidth characters.
#
# Extra spaces between words should be distributed as evenly as possible. If
# the number of spaces on a line does not divide evenly between words, the
# empty slots on the left will be assigned more spaces than the slots on the
# right.
#
# For the last line of text, it should be left-justified, and no extra space is
# inserted between words.
#
# Note:
#
# A word is defined as a character sequence consisting of non-space characters
# only.
#
# Each word's length is guaranteed to be greater than 0 and not exceed
# maxWidth.
#
# The input array words contains at least one word.
#
# Example 1:
#
# Input: words = ["This", "is", "an", "example", "of", "text",
# "justification."], maxWidth = 16
# Output:
# [
# "This is an",
# "example of text",
# "justification. "
# ]
#
# Example 2:
#
# Input: words = ["What","must","be","acknowledgment","shall","be"], maxWidth =
# 16
# Output:
# [
# "What must be",
# "acknowledgment ",
# "shall be "
# ]
# Explanation: Note that the last line is "shall be " instead of "shall be",
# because the last line must be left-justified instead of fully-justified.
# Note that the second line is also left-justified because it contains only one
# word.
#
# Example 3:
#
# Input: words =
# ["Science","is","what","we","understand","well","enough","to","explain","to","a","computer.","Art","is","everything","else","we","do"],
# maxWidth = 20
# Output:
# [
# "Science is what we",
# "understand well",
# "enough to explain to",
# "a computer. Art is",
# "everything else we",
# "do "
# ]
#
# Constraints:
#
# 1 <= words.length <= 300
#
# 1 <= words[i].length <= 20
#
# words[i] consists of only English letters and symbols.
#
# 1 <= maxWidth <= 100
#
# words[i].length <= maxWidth
#

# @lc code=start
from typing import List


class Solution:
    def fullJustify(self, words: List[str], maxWidth: int) -> List[str]:
        """
        Interview explanation:
        Greedily pack as many words as fit on each line (counting single
        spaces between them). Fully justify middle lines by distributing extra
        spaces left-to-right; left-justify the last line (and single-word
        lines).

        Algorithm:
        - Accumulate words until adding the next would exceed maxWidth.
        - Format the packed line:
          - Last line / one word: words joined by single spaces, pad right.
          - Otherwise: split extra spaces across gaps, left gaps get +1 first.
        - Continue until all words are placed.

        Complexity: O(total characters) time, O(maxWidth) per line space.
        """
        ans: List[str] = []
        line: List[str] = []
        length = 0

        def format_line(words_in_line: List[str], is_last: bool) -> str:
            if is_last or len(words_in_line) == 1:
                s = " ".join(words_in_line)
                return s + " " * (maxWidth - len(s))

            gaps = len(words_in_line) - 1
            total_spaces = maxWidth - sum(len(w) for w in words_in_line)
            space, extra = divmod(total_spaces, gaps)
            parts = []
            for i, w in enumerate(words_in_line[:-1]):
                parts.append(w)
                parts.append(" " * (space + (1 if i < extra else 0)))
            parts.append(words_in_line[-1])
            return "".join(parts)

        for w in words:
            if line and length + len(line) + len(w) > maxWidth:
                ans.append(format_line(line, False))
                line = []
                length = 0
            line.append(w)
            length += len(w)

        ans.append(format_line(line, True))
        return ans
# @lc code=end
