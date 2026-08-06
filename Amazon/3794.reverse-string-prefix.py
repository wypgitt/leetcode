#
# @lc app=leetcode id=3794 lang=python3
#
# [3794] Reverse String Prefix
#
# https://leetcode.com/problems/reverse-string-prefix/description/
#
# algorithms
# Easy (89.52%)
# Likes:    58
# Dislikes: 2
# Total Accepted:    74.6K
# Total Submissions: 83.4K
# Testcase Example:  "\"abcd\"\n2"
#
#
# You are given a string s and an integer k.
#
# Reverse the first k characters of s and return the resulting string.
#
# Example 1:
#
# Input: s = "abcd", k = 2
#
# Output: "bacd"
#
# Explanation:​​​​​​​
#
# The first k = 2 characters "ab" are reversed to "ba". The final
# resulting string is "bacd".
#
# Example 2:
#
# Input: s = "xyz", k = 3
#
# Output: "zyx"
#
# Explanation:
#
# The first k = 3 characters "xyz" are reversed to "zyx". The final
# resulting string is "zyx".
#
# Example 3:
#
# Input: s = "hey", k = 1
#
# Output: "hey"
#
# Explanation:
#
# The first k = 1 character "h" remains unchanged on reversal. The final
# resulting string is "hey".
#
# Constraints:
#
# 1 <= s.length <= 100
#
# s consists of lowercase English letters.
#
# 1 <= k <= s.length
#

# @lc code=start
class Solution:
    def reversePrefix(self, s: str, k: int) -> str:
        """
        Interview explanation:
        Reverse the prefix of length k and concatenate the untouched suffix.

        Algorithm:
        - Return s[:k][::-1] + s[k:].

        Complexity: O(n) time, O(n) space.
        """
        return s[:k][::-1] + s[k:]

    def reversePrefix_two_pointers(self, s: str, k: int) -> str:
        """
        Interview explanation:
        Alternate: two-pointer reverse on a mutable character list.

        Algorithm:
        - Convert to list; swap i,j from 0..k-1 inward; join.

        Complexity: O(n) time, O(n) space.
        """
        chars = list(s)
        i, j = 0, k - 1
        while i < j:
            chars[i], chars[j] = chars[j], chars[i]
            i += 1
            j -= 1
        return "".join(chars)
# @lc code=end
