#
# @lc app=leetcode id=2330 lang=python3
#
# [2330] Valid Palindrome IV
#
# https://leetcode.com/problems/valid-palindrome-iv/description/
#
# algorithms
# Medium (75.66%)
# Likes:    112
# Dislikes: 35
# Total Accepted:    21.4K
# Total Submissions: 28.3K
# Testcase Example:  "\"abcdba\""
#
#
# You are given a 0-indexed string s consisting of only lowercase English
# letters. In one operation, you can change any character of s to any
# other character.
#
# Return true if you can make s a palindrome after performing exactly one
# or two operations, or return false otherwise.
#
# Example 1:
#
# Input: s = "abcdba"
# Output: true
# Explanation: One way to make s a palindrome using 1 operation is:
# - Change s[2] to 'd'. Now, s = "abddba".
# One operation could be performed to make s a palindrome so return true.
#
# Example 2:
#
# Input: s = "aa"
# Output: true
# Explanation: One way to make s a palindrome using 2 operations is:
# - Change s[0] to 'b'. Now, s = "ba".
# - Change s[1] to 'b'. Now, s = "bb".
# Two operations could be performed to make s a palindrome so return true.
#
# Example 3:
#
# Input: s = "abcdef"
# Output: false
# Explanation: It is not possible to make s a palindrome using one or two
# operations so return false.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists only of lowercase English letters.
#
# @lc code=start
class Solution:
    def makePalindrome(self, s: str) -> bool:
        """
        Interview explanation:
        You may change any character (1 op each). Return whether s can become
        a palindrome using exactly one or two operations. With <=2 mismatched
        pairs this is always possible (extra ops can rewrite a matching pair
        or the center while preserving the palindrome property).

        Algorithm:
        - Two pointers count mismatched pairs; return cnt <= 2.

        Complexity: O(n) time, O(1) space.
        """
        i, j = 0, len(s) - 1
        cnt = 0
        while i < j:
            cnt += s[i] != s[j]
            i += 1
            j -= 1
        return cnt <= 2

    def makePalindrome_two_pointers(self, s: str) -> bool:
        """
        Interview explanation:
        Two-pointers mismatch count (same as primary).

        Algorithm:
        - Count differing pairs; accept if <= 2.

        Complexity: O(n) time, O(1) space.
        """
        return self.makePalindrome(s)
# @lc code=end
