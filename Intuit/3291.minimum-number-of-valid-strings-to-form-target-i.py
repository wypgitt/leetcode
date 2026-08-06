#
# @lc app=leetcode id=3291 lang=python3
#
# [3291] Minimum Number of Valid Strings to Form Target I
#
# https://leetcode.com/problems/minimum-number-of-valid-strings-to-form-target-i/description/
#
# algorithms
# Medium (22.25%)
# Likes:    183
# Dislikes: 17
# Total Accepted:    15.8K
# Total Submissions: 70.9K
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
# 1 <= words[i].length <= 5 * 10^3
#
# The input is generated such that sum(words[i].length) <= 10^5.
#
# words[i] consists only of lowercase English letters.
#
# 1 <= target.length <= 5 * 10^3
#
# target consists only of lowercase English letters.
#

# @lc code=start
from typing import List


class Solution:
    def minValidStrings(self, words: List[str], target: str) -> int:
        """
        Interview explanation:
        Valid pieces are prefixes of words. Cover target with fewest concatenations.

        Algorithm:
        - For each word, Z-array vs target → longest word-prefix match at each i.
        - max_jump[i] = farthest cover length starting at i.
        - Jump-Game II: minimum jumps to reach n, or -1.
        - Alternate: trie of words + DP from each index.

        Complexity: O((sum|w| + |words|*n)) time, O(n) space.
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

    def minValidStrings_trie(self, words: List[str], target: str) -> int:
        """
        Interview explanation:
        Trie of all words (every node is a valid prefix) plus jump DP.

        Algorithm:
        - Insert words into a trie; from each i walk target to get max_jump[i].
        - Same Jump-Game II covering.

        Complexity: O(sum|w| + n * L) time, O(sum|w|) space.
        """
        trie = {}
        for w in words:
            node = trie
            for ch in w:
                node = node.setdefault(ch, {})
        n = len(target)
        max_jump = [0] * n
        for i in range(n):
            node = trie
            j = i
            while j < n and target[j] in node:
                node = node[target[j]]
                j += 1
                max_jump[i] = j - i
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
