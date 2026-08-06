#
# @lc app=leetcode id=1616 lang=python3
#
# [1616] Split Two Strings to Make Palindrome
#
# https://leetcode.com/problems/split-two-strings-to-make-palindrome/description/
#
# algorithms
# Medium (32.58%)
# Likes:    786
# Dislikes: 260
# Total Accepted:    34.0K
# Total Submissions: 104K
# Testcase Example:  "\"x\""
#
# You are given two strings a and b of the same length. Choose an index and
# split both strings at the same index, splitting a into two strings: a_prefix
# and a_suffix where a = a_prefix + a_suffix, and splitting b into two strings:
# b_prefix and b_suffix where b = b_prefix + b_suffix. Check if a_prefix +
# b_suffix or b_prefix + a_suffix forms a palindrome.
#
# When you split a string s into s_prefix and s_suffix, either s_suffix or
# s_prefix is allowed to be empty. For example, if s = "abc", then "" + "abc",
# "a" + "bc", "ab" + "c" , and "abc" + "" are valid splits.
#
# Return true if it is possible to form a palindrome string, otherwise return
# false.
#
# Notice that x + y denotes the concatenation of strings x and y.
#
# Example 1:
#
# Input: a = "x", b = "y"
# Output: true
# Explaination: If either a or b are palindromes the answer is true since you
# can split in the following way:
# a_prefix = "", a_suffix = "x"
# b_prefix = "", b_suffix = "y"
# Then, a_prefix + b_suffix = "" + "y" = "y", which is a palindrome.
#
# Example 2:
#
# Input: a = "xbdef", b = "xecab"
# Output: false
#
# Example 3:
#
# Input: a = "ulacfd", b = "jizalu"
# Output: true
# Explaination: Split them at index 3:
# a_prefix = "ula", a_suffix = "cfd"
# b_prefix = "jiz", b_suffix = "alu"
# Then, a_prefix + b_suffix = "ula" + "alu" = "ulaalu", which is a palindrome.
#
# Constraints:
#
# 1 <= a.length, b.length <= 10^5
#
# a.length == b.length
#
# a and b consist of lowercase English letters
#

# @lc code=start
class Solution:
    def checkPalindromeFormation(self, a: str, b: str) -> bool:
        """
        Interview explanation:
        Can form palindrome by prefix of one string + suffix of the other.
        Check a-prefix|b-suffix and b-prefix|a-suffix with two-pointer helper.

        Algorithm (two pointers):
        - Helper(a,b): i=0,j=n-1; while a[i]==b[j] advance; then middle of a or b
          must be palindrome.
        - Return helper(a,b) or helper(b,a).

        Complexity: O(n) time, O(1) space.
        """
        def is_pal(s: str, i: int, j: int) -> bool:
            while i < j:
                if s[i] != s[j]:
                    return False
                i += 1
                j -= 1
            return True

        def check(x: str, y: str) -> bool:
            i, j = 0, len(x) - 1
            while i < j and x[i] == y[j]:
                i += 1
                j -= 1
            return is_pal(x, i, j) or is_pal(y, i, j)

        return check(a, b) or check(b, a)

    def checkPalindromeFormation_bruteforce_mid(self, a: str, b: str) -> bool:
        """
        Interview explanation:
        Alternate clarity version: same two-pointer idea with explicit middle checks.

        Algorithm:
        - Identical structure; separate is_palindrome helper for remaining segment.

        Complexity: O(n) time, O(1) space.
        """
        n = len(a)

        def ok(x: str, y: str) -> bool:
            i = 0
            j = n - 1
            while i < j and x[i] == y[j]:
                i += 1
                j -= 1
            return x[i : j + 1] == x[i : j + 1][::-1] or y[i : j + 1] == y[i : j + 1][::-1]

        return ok(a, b) or ok(b, a)
# @lc code=end
