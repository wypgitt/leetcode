#
# @lc app=leetcode id=520 lang=python3
#
# [520] Detect Capital
#
# https://leetcode.com/problems/detect-capital/description/
#
# algorithms
# Easy (56.9%)
# Likes:    3625
# Dislikes: 473
# Total Accepted:    589K
# Total Submissions: 1.0M
# Testcase Example:  "\"USA\""
#
# We define the usage of capitals in a word to be right when one of the
# following cases holds:
#
# All letters in this word are capitals, like "USA".
#
# All letters in this word are not capitals, like "leetcode".
#
# Only the first letter in this word is capital, like "Google".
#
# Given a string word, return true if the usage of capitals in it is right.
#
# Example 1:
#
# Input: word = "USA"
# Output: true
#
# Example 2:
#
# Input: word = "FlaG"
# Output: false
#
# Constraints:
#
# 1 <= word.length <= 100
#
# word consists of lowercase and uppercase English letters.
#

# @lc code=start
class Solution:
    def detectCapitalUse(self, word: str) -> bool:
        """
        Interview explanation:
        Valid capital usage: all uppercase, all lowercase, or only the first
        letter uppercase. Check those three cases.

        Algorithm:
        - Return word.isupper() or word.islower() or word.istitle().

        Complexity: O(n) time, O(1) space.
        """
        return word.isupper() or word.islower() or word.istitle()
# @lc code=end
