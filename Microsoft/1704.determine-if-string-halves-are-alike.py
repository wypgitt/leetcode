#
# @lc app=leetcode id=1704 lang=python3
#
# [1704] Determine if String Halves Are Alike
#
# https://leetcode.com/problems/determine-if-string-halves-are-alike/description/
#
# algorithms
# Easy (78.83%)
# Likes:    2346
# Dislikes: 127
# Total Accepted:    411K
# Total Submissions: 522K
# Testcase Example:  "\"book\""
#
# You are given a string s of even length. Split this string into two halves of
# equal lengths, and let a be the first half and b be the second half.
#
# Two strings are alike if they have the same number of vowels ('a', 'e', 'i',
# 'o', 'u', 'A', 'E', 'I', 'O', 'U'). Notice that s contains uppercase and
# lowercase letters.
#
# Return true if a and b are alike. Otherwise, return false.
#
# Example 1:
#
# Input: s = "book"
# Output: true
# Explanation: a = "bo" and b = "ok". a has 1 vowel and b has 1 vowel.
# Therefore, they are alike.
#
# Example 2:
#
# Input: s = "textbook"
# Output: false
# Explanation: a = "text" and b = "book". a has 1 vowel whereas b has 2.
# Therefore, they are not alike.
# Notice that the vowel o is counted twice.
#
# Constraints:
#
# 2 <= s.length <= 1000
#
# s.length is even.
#
# s consists of uppercase and lowercase letters.
#

# @lc code=start
class Solution:
    def halvesAreAlike(self, s: str) -> bool:
        """
        Interview explanation:
        Split string into two equal halves; compare vowel counts.

        Algorithm:
        - vowels = set(aeiouAEIOU)
        - Count vowels in s[:n//2] vs s[n//2:]

        Complexity: O(n) time, O(1) space.
        """
        vowels = set('aeiouAEIOU')
        n = len(s)
        mid = n // 2
        return sum(c in vowels for c in s[:mid]) == sum(c in vowels for c in s[mid:])
# @lc code=end
