#
# @lc app=leetcode id=1592 lang=python3
#
# [1592] Rearrange Spaces Between Words
#
# https://leetcode.com/problems/rearrange-spaces-between-words/description/
#
# algorithms
# Easy (44.32%)
# Likes:    501
# Dislikes: 354
# Total Accepted:    75.4K
# Total Submissions: 170K
# Testcase Example:  "\"  this   is  a sentence \""
#
# You are given a string text of words that are placed among some number of
# spaces. Each word consists of one or more lowercase English letters and are
# separated by at least one space. It's guaranteed that text contains at least
# one word.
#
# Rearrange the spaces so that there is an equal number of spaces between every
# pair of adjacent words and that number is maximized. If you cannot
# redistribute all the spaces equally, place the extra spaces at the end,
# meaning the returned string should be the same length as text.
#
# Return the string after rearranging the spaces.
#
# Example 1:
#
# Input: text = " this is a sentence "
# Output: "this is a sentence"
# Explanation: There are a total of 9 spaces and 4 words. We can evenly divide
# the 9 spaces between the words: 9 / (4-1) = 3 spaces.
#
# Example 2:
#
# Input: text = " practice makes perfect"
# Output: "practice makes perfect "
# Explanation: There are a total of 7 spaces and 3 words. 7 / (3-1) = 3 spaces
# plus 1 extra space. We place this extra space at the end of the string.
#
# Constraints:
#
# 1 <= text.length <= 100
#
# text consists of lowercase English letters and ' '.
#
# text contains at least one word.
#

# @lc code=start
class Solution:
    def reorderSpaces(self, text: str) -> str:
        """
        Interview explanation:
        Redistribute spaces evenly between words; leftover spaces go to the end.
        If one word, all spaces after it.

        Algorithm:
        - words = text.split(); spaces = text.count(' ')
        - if len(words)==1: return words[0] + ' '*spaces
        - gap = spaces // (len(words)-1); rem = spaces % (len(words)-1)
        - join words with ' '*gap; append ' '*rem

        Complexity: O(n) time/space.
        """
        words = text.split()
        spaces = text.count(" ")
        if len(words) == 1:
            return words[0] + " " * spaces
        gap, rem = divmod(spaces, len(words) - 1)
        return (" " * gap).join(words) + " " * rem
# @lc code=end

