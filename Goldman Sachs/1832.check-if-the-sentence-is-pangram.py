#
# @lc app=leetcode id=1832 lang=python3
#
# [1832] Check if the Sentence Is Pangram
#
# https://leetcode.com/problems/check-if-the-sentence-is-pangram/description/
#
# algorithms
# Easy (84.3%)
# Likes:    3051
# Dislikes: 67
# Total Accepted:    579K
# Total Submissions: 687K
# Testcase Example:  "\"thequickbrownfoxjumpsoverthelazydog\""
#
# A pangram is a sentence where every letter of the English alphabet appears at
# least once.
#
# Given a string sentence containing only lowercase English letters, return
# true if sentence is a pangram, or false otherwise.
#
# Example 1:
#
# Input: sentence = "thequickbrownfoxjumpsoverthelazydog"
# Output: true
# Explanation: sentence contains at least one of every letter of the English
# alphabet.
#
# Example 2:
#
# Input: sentence = "leetcode"
# Output: false
#
# Constraints:
#
# 1 <= sentence.length <= 1000
#
# sentence consists of lowercase English letters.
#

# @lc code=start
class Solution:
    def checkIfPangram(self, sentence: str) -> bool:
        """
        Interview explanation:
        Pangram iff all 26 letters appear.

        Algorithm (set):
        - return len(set(sentence))==26.

        Complexity: O(n) time, O(1) space.
        """
        return len(set(sentence)) == 26

    def checkIfPangram_bitmask(self, sentence: str) -> bool:
        """
        Interview explanation:
        Alternate: bit mask of seen letters; full when mask==(1<<26)-1.

        Algorithm (bitmask):
        - OR 1<<(c-'a'); compare to mask.

        Complexity: O(n) time, O(1) space.
        """
        mask = 0
        for ch in sentence:
            mask |= 1 << (ord(ch) - 97)
        return mask == (1 << 26) - 1
# @lc code=end
