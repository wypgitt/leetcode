#
# @lc app=leetcode id=3121 lang=python3
#
# [3121] Count the Number of Special Characters II
#
# https://leetcode.com/problems/count-the-number-of-special-characters-ii/description/
#
# algorithms
# Medium (60.48%)
# Likes:    463
# Dislikes: 25
# Total Accepted:    170.4K
# Total Submissions: 281.8K
# Testcase Example:  "\"aaAbcBC\""
#
#
# You are given a string word. A letter c is called special if it appears
# both in lowercase and uppercase in word, and every lowercase occurrence
# of c appears before the first uppercase occurrence of c.
#
# Return the number of special letters in word.
#
# Example 1:
#
# Input: word = "aaAbcBC"
#
# Output: 3
#
# Explanation:
#
# The special characters are 'a', 'b', and 'c'.
#
# Example 2:
#
# Input: word = "abc"
#
# Output: 0
#
# Explanation:
#
# There are no special characters in word.
#
# Example 3:
#
# Input: word = "AbBCab"
#
# Output: 0
#
# Explanation:
#
# There are no special characters in word.
#
# Constraints:
#
# 1 <= word.length <= 2 * 10^5
#
# word consists of only lowercase and uppercase English letters.
#

# @lc code=start
class Solution:
    def numberOfSpecialChars(self, word: str) -> int:
        """
        Interview explanation:
        Special letter: appears in both cases, and every lowercase occurrence
        is before the first uppercase occurrence.

        Algorithm:
        - Track last lowercase index and first uppercase index per letter.
        - Count letters with last_lower < first_upper.

        Complexity: O(n) time, O(1) space.
        """
        last_lower = {}
        first_upper = {}
        for i, c in enumerate(word):
            if c.islower():
                last_lower[c] = i
            else:
                cl = c.lower()
                if cl not in first_upper:
                    first_upper[cl] = i
        return sum(
            1
            for c, i in last_lower.items()
            if c in first_upper and i < first_upper[c]
        )
# @lc code=end
