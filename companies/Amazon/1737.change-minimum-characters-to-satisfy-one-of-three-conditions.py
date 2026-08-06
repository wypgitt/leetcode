#
# @lc app=leetcode id=1737 lang=python3
#
# [1737] Change Minimum Characters to Satisfy One of Three Conditions
#
# https://leetcode.com/problems/change-minimum-characters-to-satisfy-one-of-three-conditions/description/
#
# algorithms
# Medium (38.18%)
# Likes:    339
# Dislikes: 346
# Total Accepted:    17.1K
# Total Submissions: 44.7K
# Testcase Example:  "\"aba\""
#
# You are given two strings a and b that consist of lowercase letters. In one
# operation, you can change any character in a or b to any lowercase letter.
#
# Your goal is to satisfy one of the following three conditions:
#
# Every letter in a is strictly less than every letter in b in the alphabet.
#
# Every letter in b is strictly less than every letter in a in the alphabet.
#
# Both a and b consist of only one distinct letter.
#
# Return the minimum number of operations needed to achieve your goal.
#
# Example 1:
#
# Input: a = "aba", b = "caa"
# Output: 2
# Explanation: Consider the best way to make each condition true:
# 1) Change b to "ccc" in 2 operations, then every letter in a is less than
# every letter in b.
# 2) Change a to "bbb" and b to "aaa" in 3 operations, then every letter in b
# is less than every letter in a.
# 3) Change a to "aaa" and b to "aaa" in 2 operations, then a and b consist of
# one distinct letter.
# The best way was done in 2 operations (either condition 1 or condition 3).
#
# Example 2:
#
# Input: a = "dabadd", b = "cda"
# Output: 3
# Explanation: The best way is to make condition 1 true by changing b to "eee".
#
# Constraints:
#
# 1 <= a.length, b.length <= 10^5
#
# a and b consist only of lowercase letters.
#

# @lc code=start
from collections import Counter


class Solution:
    def minCharacters(self, a: str, b: str) -> int:
        """
        Interview explanation:
        Three goals: make all of a strictly below all of b via some threshold;
        swap roles; or make both strings a single identical character. Min changes.

        Algorithm:
        - Freq counts; condition 3 = |a|+|b| - max_c (ca[c]+cb[c]).
        - For each split letter, compute changes for a<b and b<a via prefix counts.

        Complexity: O(|a|+|b|+26) time, O(26) space.
        """
        ca = Counter(a)
        cb = Counter(b)
        na, nb = len(a), len(b)
        ans = na + nb - max(ca[chr(c)] + cb[chr(c)] for c in range(ord("a"), ord("z") + 1))
        pa = [0] * 27
        pb = [0] * 27
        for i, ch in enumerate(map(chr, range(ord("a"), ord("z") + 1)), 1):
            pa[i] = pa[i - 1] + ca[ch]
            pb[i] = pb[i - 1] + cb[ch]
        for t in range(1, 26):
            ans = min(ans, (pa[26] - pa[t]) + pb[t])
            ans = min(ans, (pb[26] - pb[t]) + pa[t])
        return ans
# @lc code=end
