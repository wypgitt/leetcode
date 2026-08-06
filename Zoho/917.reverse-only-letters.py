#
# @lc app=leetcode id=917 lang=python3
#
# [917] Reverse Only Letters
#
# https://leetcode.com/problems/reverse-only-letters/description/
#
# algorithms
# Easy (68.87%)
# Likes:    2474
# Dislikes: 87
# Total Accepted:    345K
# Total Submissions: 501K
# Testcase Example:  "\"ab-cd\""
#
# Given a string s, reverse the string according to the following rules:
#
# All the characters that are not English letters remain in the same position.
#
# All the English letters (lowercase or uppercase) should be reversed.
#
# Return s after reversing it.
#
# Example 1:
#
# Input: s = "ab-cd"
# Output: "dc-ba"
#
# Example 2:
#
# Input: s = "a-bC-dEf-ghIj"
# Output: "j-Ih-gfE-dCba"
#
# Example 3:
#
# Input: s = "Test1ng-Leet=code-Q!"
# Output: "Qedo1ct-eeLg=ntse-T!"
#
# Constraints:
#
# 1 <= s.length <= 100
#
# s consists of characters with ASCII values in the range [33, 122].
#
# s does not contain '\"' or '\\'.
#

# @lc code=start
class Solution:
    def reverseOnlyLetters(self, s: str) -> str:
        """
        Interview explanation:
        Reverse only alphabetic characters; keep others fixed. Two pointers
        skip non-letters and swap letters.

        Algorithm (two pointers):
        - chars=list(s); l,r. While l<r: skip non-alpha; swap; move.

        Complexity: O(n) time, O(n) space for list.
        """
        chars = list(s)
        l, r = 0, len(chars) - 1
        while l < r:
            if not chars[l].isalpha():
                l += 1
            elif not chars[r].isalpha():
                r -= 1
            else:
                chars[l], chars[r] = chars[r], chars[l]
                l += 1
                r -= 1
        return "".join(chars)
# @lc code=end

