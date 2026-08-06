#
# @lc app=leetcode id=3292 lang=python3
#
# [3292] Minimum Number of Valid Strings to Form Target II
#
# https://leetcode.com/problems/minimum-number-of-valid-strings-to-form-target-ii/description/
#
# algorithms
# Hard (21.07%)
# Likes:    89
# Dislikes: 10
# Total Accepted:    5.9K
# Total Submissions: 28K
# Testcase Example:  "[\"abc\",\"aaaaa\",\"bcdef\"]\n\"aabcdabc\""
#
#
# You are given an array of strings words and a string target.
#
# A string x is called valid if x is a prefix of any string in words.
#
# Return the minimum number of valid strings that can be concatenated to
# form target. If it is not possible to form target, return -1.
#
# Example 1:
#
# Input: words = ["abc","aaaaa","bcdef"], target = "aabcdabc"
#
# Output: 3
#
# Explanation:
#
# The target string can be formed by concatenating:
#
# Prefix of length 2 of words[1], i.e. "aa".
#
# Prefix of length 3 of words[2], i.e. "bcd".
#
# Prefix of length 3 of words[0], i.e. "abc".
#
# Example 2:
#
# Input: words = ["abababab","ab"], target = "ababaababa"
#
# Output: 2
#
# Explanation:
#
# The target string can be formed by concatenating:
#
# Prefix of length 5 of words[0], i.e. "ababa".
#
# Prefix of length 5 of words[0], i.e. "ababa".
#
# Example 3:
#
# Input: words = ["abcdef"], target = "xyz"
#
# Output: -1
#
# Constraints:
#
# 1 <= words.length <= 100
#
# 1 <= words[i].length <= 5 * 10^4
#
# The input is generated such that sum(words[i].length) <= 10^5.
#
# words[i] consists only of lowercase English letters.
#
# 1 <= target.length <= 5 * 10^4
#
# target consists only of lowercase English letters.
#

# @lc code=start
from typing import List


class Solution:
    def minValidStrings(self, words: List[str], target: str) -> int:
        """
        Interview explanation:
        Same as I but larger limits: need near-linear covering of target by
        word prefixes.

        Algorithm:
        - Z-algorithm per word against target for max prefix match at each index.
        - Jump-Game II on max_jump to get minimum concatenations.

        Complexity: O(sum|w| + |words|*n) time, O(n) space.
        """
        n = len(target)
        max_jump = [0] * n

        def z_func(s: str) -> List[int]:
            m = len(s)
            z = [0] * m
            l = r = 0
            for i in range(1, m):
                if i <= r:
                    z[i] = min(r - i + 1, z[i - l])
                while i + z[i] < m and s[z[i]] == s[i + z[i]]:
                    z[i] += 1
                if i + z[i] - 1 > r:
                    l, r = i, i + z[i] - 1
            return z

        for w in words:
            z = z_func(w + "#" + target)
            base = len(w) + 1
            for i in range(n):
                if z[base + i] > max_jump[i]:
                    max_jump[i] = z[base + i]

        jumps = 0
        cur_end = 0
        farthest = 0
        for i in range(n):
            if i > farthest:
                return -1
            farthest = max(farthest, i + max_jump[i])
            if i == cur_end:
                jumps += 1
                cur_end = farthest
                if cur_end >= n:
                    return jumps
        return -1
# @lc code=end
