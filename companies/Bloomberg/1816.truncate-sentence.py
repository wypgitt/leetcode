#
# @lc app=leetcode id=1816 lang=python3
#
# [1816] Truncate Sentence
#
# https://leetcode.com/problems/truncate-sentence/description/
#
# algorithms
# Easy (87.02%)
# Likes:    1242
# Dislikes: 34
# Total Accepted:    246K
# Total Submissions: 282K
# Testcase Example:  "\"Hello how are you Contestant\""
#
# A sentence is a list of words that are separated by a single space with no
# leading or trailing spaces. Each of the words consists of only uppercase and
# lowercase English letters (no punctuation).
#
# For example, "Hello World", "HELLO", and "hello world hello world" are all
# sentences.
#
# You are given a sentence s and an integer k. You want to truncate s such that
# it contains only the first k words. Return s after truncating it.
#
# Example 1:
#
# Input: s = "Hello how are you Contestant", k = 4
# Output: "Hello how are you"
# Explanation:
# The words in s are ["Hello", "how", "are", "you", "Contestant"].
# The first 4 words are ["Hello", "how", "are", "you"].
# Hence, you should return "Hello how are you".
#
# Example 2:
#
# Input: s = "What is the solution to this problem", k = 4
# Output: "What is the solution"
# Explanation:
# The words in s are ["What", "is" "the", "solution", "to", "this", "problem"].
# The first 4 words are ["What", "is", "the", "solution"].
# Hence, you should return "What is the solution".
#
# Example 3:
#
# Input: s = "chopper is not a tanuki", k = 5
# Output: "chopper is not a tanuki"
#
# Constraints:
#
# 1 <= s.length <= 500
#
# k is in the range [1, the number of words in s].
#
# s consist of only lowercase and uppercase English letters and spaces.
#
# The words in s are separated by a single space.
#
# There are no leading or trailing spaces.
#

# @lc code=start
class Solution:
    def truncateSentence(self, s: str, k: int) -> str:
        """
        Interview explanation:
        Keep first k words of sentence s.

        Algorithm (split):
        - return ' '.join(s.split()[:k]).

        Complexity: O(n) time, O(n) space.
        """
        return ' '.join(s.split()[:k])

    def truncateSentence_scan(self, s: str, k: int) -> str:
        """
        Interview explanation:
        Alternate without full split list: scan spaces until k words.

        Algorithm (scan):
        - Count spaces; cut at k-th space or end.

        Complexity: O(n) time, O(1) extra.
        """
        spaces = 0
        for i, ch in enumerate(s):
            if ch == ' ':
                spaces += 1
                if spaces == k:
                    return s[:i]
        return s
# @lc code=end
