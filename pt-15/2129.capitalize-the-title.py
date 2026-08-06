#
# @lc app=leetcode id=2129 lang=python3
#
# [2129] Capitalize the Title
#
# https://leetcode.com/problems/capitalize-the-title/description/
#
# algorithms
# Easy (68.36%)
# Likes:    825
# Dislikes: 55
# Total Accepted:    103.2K
# Total Submissions: 151K
# Testcase Example:  "\"capiTalIze tHe titLe\""
#
# You are given a string title consisting of one or more words separated by a
# single space, where each word consists of English letters. Capitalize the
# string by changing the capitalization of each word such that:
#
#
# If the length of the word is 1 or 2 letters, change all letters to lowercase.
#
#
# Otherwise, change the first letter to uppercase and the remaining letters to
# lowercase.
#
# Return the capitalized title.
#
#
#
# Example 1:
#
# Input: title = "capiTalIze tHe titLe"
# Output: "Capitalize The Title"
# Explanation:
# Since all the words have a length of at least 3, the first letter of each word
# is uppercase, and the remaining letters are lowercase.
#
# Example 2:
#
# Input: title = "First leTTeR of EACH Word"
# Output: "First Letter of Each Word"
# Explanation:
# The word "of" has length 2, so it is all lowercase.
# The remaining words have a length of at least 3, so the first letter of each
# remaining word is uppercase, and the remaining letters are lowercase.
#
# Example 3:
#
# Input: title = "i lOve leetcode"
# Output: "i Love Leetcode"
# Explanation:
# The word "i" has length 1, so it is lowercase.
# The remaining words have a length of at least 3, so the first letter of each
# remaining word is uppercase, and the remaining letters are lowercase.
#
#
#
# Constraints:
#
#
# 1 <= title.length <= 100
#
#
# title consists of words separated by a single space without any leading or
# trailing spaces.
#
#
# Each word consists of uppercase and lowercase English letters and is
# non-empty.
#


# @lc code=start
class Solution:
    def capitalizeTitle(self, title: str) -> str:
        """
        Interview explanation:
        Words of length 1-2 → all lowercase; longer → first upper, rest lower.

        Algorithm:
        - Split; transform each word; join.

        Complexity: O(n) time, O(n) space.
        """
        parts = []
        for w in title.split():
            if len(w) <= 2:
                parts.append(w.lower())
            else:
                parts.append(w[:1].upper() + w[1:].lower())
        return ' '.join(parts)
# @lc code=end

