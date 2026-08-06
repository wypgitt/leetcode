#
# @lc app=leetcode id=3734 lang=python3
#
# [3734] Lexicographically Smallest Palindromic Permutation Greater Than Target
#
# https://leetcode.com/problems/lexicographically-smallest-palindromic-permutation-greater-than-target/description/
#
# algorithms
# Hard (25.66%)
# Likes:    40
# Dislikes: 5
# Total Accepted:    5.3K
# Total Submissions: 20.8K
# Testcase Example:  "\"baba\"\n\"abba\""
#
#
# You are given two strings s and target, each of length n, consisting of
# lowercase English letters.
#
# Return the lexicographically smallest string that is both a palindromic
# permutation of s and strictly greater than target. If no such
# permutation exists, return an empty string.
#
# Example 1:
#
# Input: s = "baba", target = "abba"
#
# Output: "baab"
#
# Explanation:
#
# The palindromic permutations of s (in lexicographical order) are "abba"
# and "baab".
#
# The lexicographically smallest permutation that is strictly greater than
# target is "baab".
#
# Example 2:
#
# Input: s = "baba", target = "bbaa"
#
# Output: ""
#
# Explanation:
#
# The palindromic permutations of s (in lexicographical order) are "abba"
# and "baab".
#
# None of them is lexicographically strictly greater than target.
# Therefore, the answer is "".
#
# Example 3:
#
# Input: s = "abc", target = "abb"
#
# Output: ""
#
# Explanation:
#
# s has no palindromic permutations. Therefore, the answer is "".
#
# Example 4:
#
# Input: s = "aac", target = "abb"
#
# Output: "aca"
#
# Explanation:
#
# The only palindromic permutation of s is "aca".
#
# "aca" is strictly greater than target. Therefore, the answer is "aca".
#
# Constraints:
#
# 1 <= n == s.length == target.length <= 300
#
# s and target consist of only lowercase English letters.
#

# @lc code=start
class Solution:
    def lexPalindromicPermutation(self, s: str, target: str) -> str:
        """
        Interview explanation:
        Palindromes are determined by the first half (plus optional middle).
        Try to match target's prefix with available letter pairs; if that
        palindrome is not strictly greater, bump the first half like next
        permutation and fill the rest greedily smallest.

        Algorithm:
        - Reject if more than one odd count.
        - Reserve the odd char as middle when n is odd.
        - Walk target's first half consuming pairs; on success, mirror and
          compare to target.
        - Otherwise backtrack, raise a half-position to the next available
          letter, then fill remaining pairs ascending.

        Complexity: O(n) time, O(1) extra space beyond the answer.
        """
        cnt = [0] * 26
        for ch in s:
            cnt[ord(ch) - 97] += 1
        if sum(c % 2 for c in cnt) > 1:
            return ""
        n = len(target)
        mid = -1
        if n % 2:
            mid = next(i for i, c in enumerate(cnt) if c % 2)
            cnt[mid] -= 1
        half = n // 2
        result = []
        matched = True
        for i in range(half):
            idx = ord(target[i]) - 97
            cnt[idx] -= 2
            result.append(target[i])
            if cnt[idx] < 0:
                matched = False
                break
        if matched:
            ret = self._mirror(result, mid, n)
            if ret > target:
                return ret
        while result:
            c = ord(result.pop()) - 97
            cnt[c] += 2
            for i in range(c + 1, 26):
                if cnt[i] < 2:
                    continue
                cnt[i] -= 2
                result.append(chr(97 + i))
                for j in range(26):
                    while cnt[j] >= 2:
                        cnt[j] -= 2
                        result.append(chr(97 + j))
                return self._mirror(result, mid, n)
        return ""

    def _mirror(self, half_chars: list, mid: int, n: int) -> str:
        """Build a palindrome from the first-half letters and optional middle."""
        left = "".join(half_chars)
        if n % 2:
            return left + chr(97 + mid) + left[::-1]
        return left + left[::-1]

    def lexPalindromicPermutation_generate(self, s: str, target: str) -> str:
        """
        Interview explanation:
        Alternate for small alphabets: build the smallest palindromic
        permutation, then the next ones until > target (still pair-driven).

        Algorithm:
        - Delegate to the greedy next-half method above (same result).

        Complexity: O(n) time, O(n) space.
        """
        return self.lexPalindromicPermutation(s, target)
# @lc code=end

