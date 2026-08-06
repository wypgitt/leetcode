#
# @lc app=leetcode id=3720 lang=python3
#
# [3720] Lexicographically Smallest Permutation Greater Than Target
#
# https://leetcode.com/problems/lexicographically-smallest-permutation-greater-than-target/description/
#
# algorithms
# Medium (26.98%)
# Likes:    116
# Dislikes: 7
# Total Accepted:    13.3K
# Total Submissions: 49.5K
# Testcase Example:  "\"abc\"\n\"bba\""
#
#
# You are given two strings s and target, both having length n, consisting
# of lowercase English letters.
#
# Return the lexicographically smallest permutation of s that is strictly
# greater than target. If no permutation of s is lexicographically
# strictly greater than target, return an empty string.
#
# A string a is lexicographically strictly greater than a string b (of the
# same length) if in the first position where a and b differ, string a has
# a letter that appears later in the alphabet than the corresponding
# letter in b.
#
# Example 1:
#
# Input: s = "abc", target = "bba"
#
# Output: "bca"
#
# Explanation:
#
# The permutations of s (in lexicographical order) are "abc", "acb",
# "bac", "bca", "cab", and "cba".
#
# The lexicographically smallest permutation that is strictly greater than
# target is "bca".
#
# Example 2:
#
# Input: s = "leet", target = "code"
#
# Output: "eelt"
#
# Explanation:
#
# The permutations of s (in lexicographical order) are "eelt", "eetl",
# "elet", "elte", "etel", "etle", "leet", "lete", "ltee", "teel", "tele",
# and "tlee".
#
# The lexicographically smallest permutation that is strictly greater than
# target is "eelt".
#
# Example 3:
#
# Input: s = "baba", target = "bbaa"
#
# Output: ""
#
# Explanation:
#
# The permutations of s (in lexicographical order) are "aabb", "abab",
# "abba", "baab", "baba", and "bbaa".
#
# None of them is lexicographically strictly greater than target.
# Therefore, the answer is "".
#
# Constraints:
#
# 1 <= s.length == target.length <= 300
#
# s and target consist of only lowercase English letters.
#

# @lc code=start

from collections import Counter


class Solution:
    def lexGreaterPermutation(self, s: str, target: str) -> str:
        """
        Interview explanation:
        Build the smallest permutation of s that is strictly greater than target
        by matching the longest possible prefix, then raising one position and
        filling the suffix with the smallest remaining multiset.

        Algorithm:
        - Walk positions left-to-right with a mutable Counter of s.
        - At each i, try the smallest available char > target[i], then append
          the sorted remainder; keep the global minimum candidate.
        - If target[i] is still available, place it and continue; else stop.
        - If no raise succeeded, return "".

        Complexity: O(n * Sigma) time, O(Sigma) space (Sigma = 26).
        """
        n = len(s)
        cnt = Counter(s)
        best = None
        prefix: list[str] = []

        for i in range(n):
            for c in sorted(cnt):
                if cnt[c] and c > target[i]:
                    rem = cnt.copy()
                    rem[c] -= 1
                    if rem[c] == 0:
                        del rem[c]
                    rest = "".join(ch * rem[ch] for ch in sorted(rem))
                    cand = "".join(prefix) + c + rest
                    if best is None or cand < best:
                        best = cand
                    break
            if cnt[target[i]]:
                cnt[target[i]] -= 1
                if cnt[target[i]] == 0:
                    del cnt[target[i]]
                prefix.append(target[i])
            else:
                break

        return best if best is not None else ""
# @lc code=end
