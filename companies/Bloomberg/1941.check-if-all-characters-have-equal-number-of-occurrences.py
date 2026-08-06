#
# @lc app=leetcode id=1941 lang=python3
#
# [1941] Check if All Characters Have Equal Number of Occurrences
#
# https://leetcode.com/problems/check-if-all-characters-have-equal-number-of-occurrences/description/
#
# algorithms
# Easy (79.62%)
# Likes:    1044
# Dislikes: 29
# Total Accepted:    185K
# Total Submissions: 232K
# Testcase Example:  "\"abacbc\""
#
# Given a string s, return true if s is a good string, or false otherwise.
#
# A string s is good if all the characters that appear in s have the same
# number of occurrences (i.e., the same frequency).
#
# Example 1:
#
# Input: s = "abacbc"
# Output: true
# Explanation: The characters that appear in s are 'a', 'b', and 'c'. All
# characters occur 2 times in s.
#
# Example 2:
#
# Input: s = "aaabb"
# Output: false
# Explanation: The characters that appear in s are 'a' and 'b'.
# 'a' occurs 3 times while 'b' occurs 2 times, which is not the same number of
# times.
#
# Constraints:
#
# 1 <= s.length <= 1000
#
# s consists of lowercase English letters.
#

# @lc code=start
from collections import Counter


class Solution:
    def areOccurrencesEqual(self, s: str) -> bool:
        """
        Interview explanation:
        Good string iff every distinct character has the same frequency.

        Algorithm:
        - Counter values; len(set(counts)) == 1.

        Complexity: O(n) time, O(1) alphabet space.
        """
        c = Counter(s)
        return len(set(c.values())) == 1
# @lc code=end
