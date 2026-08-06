#
# @lc app=leetcode id=1750 lang=python3
#
# [1750] Minimum Length of String After Deleting Similar Ends
#
# https://leetcode.com/problems/minimum-length-of-string-after-deleting-similar-ends/description/
#
# algorithms
# Medium (56.16%)
# Likes:    1334
# Dislikes: 113
# Total Accepted:    192K
# Total Submissions: 342K
# Testcase Example:  "\"ca\""
#
# Given a string s consisting only of characters 'a', 'b', and 'c'. You are
# asked to apply the following algorithm on the string any number of times:
#
# Pick a non-empty prefix from the string s where all the characters in the
# prefix are equal.
#
# Pick a non-empty suffix from the string s where all the characters in this
# suffix are equal.
#
# The prefix and the suffix should not intersect at any index.
#
# The characters from the prefix and suffix must be the same.
#
# Delete both the prefix and the suffix.
#
# Return the minimum length of s after performing the above operation any
# number of times (possibly zero times).
#
# Example 1:
#
# Input: s = "ca"
# Output: 2
# Explanation: You can't remove any characters, so the string stays as is.
#
# Example 2:
#
# Input: s = "cabaabac"
# Output: 0
# Explanation: An optimal sequence of operations is:
# - Take prefix = "c" and suffix = "c" and remove them, s = "abaaba".
# - Take prefix = "a" and suffix = "a" and remove them, s = "baab".
# - Take prefix = "b" and suffix = "b" and remove them, s = "aa".
# - Take prefix = "a" and suffix = "a" and remove them, s = "".
#
# Example 3:
#
# Input: s = "aabccabba"
# Output: 3
# Explanation: An optimal sequence of operations is:
# - Take prefix = "aa" and suffix = "a" and remove them, s = "bccabb".
# - Take prefix = "b" and suffix = "bb" and remove them, s = "cca".
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s only consists of characters 'a', 'b', and 'c'.
#

# @lc code=start
class Solution:
    def minimumLength(self, s: str) -> int:
        """
        Interview explanation:
        While both ends share a character, delete the whole run of that character
        from both ends. Two pointers.

        Algorithm:
        - l,r pointers; while l<r and s[l]==s[r], strip that char from both sides.
        - Return remaining length r-l+1.

        Complexity: O(n) time, O(1) space.
        """
        l, r = 0, len(s) - 1
        while l < r and s[l] == s[r]:
            ch = s[l]
            while l <= r and s[l] == ch:
                l += 1
            while l <= r and s[r] == ch:
                r -= 1
        return max(0, r - l + 1)
# @lc code=end
