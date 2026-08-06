#
# @lc app=leetcode id=3518 lang=python3
#
# [3518] Smallest Palindromic Rearrangement II
#
# https://leetcode.com/problems/smallest-palindromic-rearrangement-ii/description/
#
# algorithms
# Hard (44.10%)
# Likes:    308
# Dislikes: 27
# Total Accepted:    73.8K
# Total Submissions: 167.3K
# Testcase Example:  "\"abba\"\n2"
#
#
# You are given a palindromic string s and an integer k.
#
# Return the k-th lexicographically smallest palindromic permutation of s.
# If there are fewer than k distinct palindromic permutations, return an
# empty string.
#
# Note: Different rearrangements that yield the same palindromic string
# are considered identical and are counted once.
#
# Example 1:
#
# Input: s = "abba", k = 2
#
# Output: "baab"
#
# Explanation:
#
# The two distinct palindromic rearrangements of "abba" are "abba" and
# "baab".
#
# Lexicographically, "abba" comes before "baab". Since k = 2, the output
# is "baab".
#
# Example 2:
#
# Input: s = "aa", k = 2
#
# Output: ""
#
# Explanation:
#
# There is only one palindromic rearrangement: "aa".
#
# The output is an empty string since k = 2 exceeds the number of possible
# rearrangements.
#
# Example 3:
#
# Input: s = "bacab", k = 1
#
# Output: "abcba"
#
# Explanation:
#
# The two distinct palindromic rearrangements of "bacab" are "abcba" and
# "bacab".
#
# Lexicographically, "abcba" comes before "bacab". Since k = 1, the output
# is "abcba".
#
# Constraints:
#
# 1 <= s.length <= 10^4
#
# s consists of lowercase English letters.
#
# s is guaranteed to be palindromic.
#
# 1 <= k <= 10^6
#

# @lc code=start
import collections


class Solution:
    def smallestPalindrome(self, s: str, k: int) -> str:
        """
        Interview explanation:
        Among distinct palindromic anagrams, return the k-th lexicographically
        smallest (1-indexed). Construct the left half greedily: try each letter
        and skip by multinomial counts of remaining arrangements.

        Algorithm:
        - halfCount[c] = freq[c]//2; mid = odd letter.
        - Cap combination counts at k; for each position try letters in order,
          subtracting arrangement counts when skipping.

        Complexity: O(n * 26 * 26) time with O(1) nCk per try; O(n) space.
        """
        MAX = 10**6 + 1
        cnt = collections.Counter(s)
        half = [0] * 26
        mid = ""
        for c, f in cnt.items():
            half[ord(c) - 97] = f // 2
            if f % 2:
                mid = c

        def nCk(n: int, r: int) -> int:
            if r < 0 or r > n:
                return 0
            r = min(r, n - r)
            res = 1
            for i in range(r):
                res = res * (n - i) // (i + 1)
                if res >= MAX:
                    return MAX
            return res

        def arrangements(h: list) -> int:
            total = sum(h)
            res = 1
            for f in h:
                res *= nCk(total, f)
                if res >= MAX:
                    return MAX
                total -= f
            return res

        if arrangements(half) < k:
            return ""

        left = []
        half_len = sum(half)
        for _ in range(half_len):
            for i in range(26):
                if half[i] == 0:
                    continue
                half[i] -= 1
                ways = arrangements(half)
                if ways >= k:
                    left.append(chr(97 + i))
                    break
                k -= ways
                half[i] += 1
        return "".join(left) + mid + "".join(reversed(left))
# @lc code=end
