#
# @lc app=leetcode id=3120 lang=python3
#
# [3120] Count the Number of Special Characters I
#
# https://leetcode.com/problems/count-the-number-of-special-characters-i/description/
#
# algorithms
# Easy (77.33%)
# Likes:    394
# Dislikes: 12
# Total Accepted:    200.3K
# Total Submissions: 259K
# Testcase Example:  "\"aaAbcBC\""
#
#
# You are given a string word. A letter is called special if it appears
# both in lowercase and uppercase in word.
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
# The special characters in word are 'a', 'b', and 'c'.
#
# Example 2:
#
# Input: word = "abc"
#
# Output: 0
#
# Explanation:
#
# No character in word appears in uppercase.
#
# Example 3:
#
# Input: word = "abBCab"
#
# Output: 1
#
# Explanation:
#
# The only special character in word is 'b'.
#
# Constraints:
#
# 1 <= word.length <= 50
#
# word consists of only lowercase and uppercase English letters.
#

# @lc code=start
class Solution:
    def numberOfSpecialChars(self, word: str) -> int:
        """
        Interview explanation:
        A letter is special if it appears in both lowercase and uppercase.

        Algorithm:
        - Build lower/upper letter sets; return size of intersection.

        Complexity: O(n) time, O(1) space (|Σ| ≤ 26).
        """
        lower = {c for c in word if c.islower()}
        upper = {c.lower() for c in word if c.isupper()}
        return len(lower & upper)

    def numberOfSpecialChars_bitmask(self, word: str) -> int:
        """
        Interview explanation:
        Same check with bitmasks for lower/upper presence.

        Algorithm:
        - OR bits for a–z lower and upper; AND masks and popcount.

        Complexity: O(n) time, O(1) space.
        """
        lo = up = 0
        for c in word:
            if c.islower():
                lo |= 1 << (ord(c) - ord("a"))
            else:
                up |= 1 << (ord(c) - ord("A"))
        return (lo & up).bit_count()
# @lc code=end
