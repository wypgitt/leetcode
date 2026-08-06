#
# @lc app=leetcode id=3999 lang=python3
#
# [3999] Minimum Number of String Groups Through Transformations
#
# https://leetcode.com/problems/minimum-number-of-string-groups-through-transformations/description/
#
# algorithms
# Hard (47.95%)
# Likes:    30
# Dislikes: 3
# Total Accepted:    7.3K
# Total Submissions: 15.3K
# Testcase Example:  "[\"ntgwz\",\"zwntg\"]"
#
#
# You are given an array of strings words.
#
# Define a transformation on a string s as follows:
#
# Let E be the subsequence of characters at even indices of s.
#
# Let O be the subsequence of characters at odd indices of s.
#
# Independently cyclically shift E and O by any number of positions to the
# right, possibly zero.
#
# Reconstruct the string by placing the shifted E characters back into
# even indices and the shifted O characters back into odd indices.
#
# Two strings are equivalent if one can be transformed into the other by a
# single transformation.
#
# Partition words into the minimum number of groups such that:
#
# Every string belongs to exactly one group.
#
# Every pair of strings in the same group are equivalent.
#
# Return an integer denoting the minimum number of groups.
#
# Example 1:
#
# Input: words = ["ntgwz","zwntg"]
#
# Output: 1
#
# Explanation:
#
# For "ntgwz", the even-index subsequence is "ngz" and the odd-index
# subsequence is "tw".
#
# Shift "ngz" right by 1 position to obtain "zng", and shift "tw" right by
# 1 position to obtain "wt".
#
# After reconstructing the string, we obtain "zwntg".
#
# Therefore, both strings are equivalent and belong to the same group.
#
# Example 2:
#
# Input: words = ["abc","cab","bac","acb","bca","cba"]
#
# Output: 3
#
# Explanation:
#
# The strings can be partitioned into the following groups:
#
# ["abc","cba"]
#
# ["cab","bac"]
#
# ["acb","bca"]
#
# Example 3:
#
# Input: words = ["leet","abb","bab","deed","edde","code","bba"]
#
# Output: 5
#
# Explanation:
#
# The strings can be partitioned into the following groups:
#
# ["abb","bba"]
#
# ["deed","edde"]
#
# ["leet"]
#
# ["bab"]
#
# ["code"]
#
# ​​​​​​​​​​​​​​All pairs of strings in each group are equivalent.
#
# Constraints:
#
# 1 <= words.length <= 10^5
#
# 1 <= words[i].length <= 5 * 10^5
#
# The sum of words[i].length does not exceed 5 * 10^5.
#
# words[i] consist of lowercase English letters.
#

# @lc code=start
from typing import List


class Solution:
    def minimumGroups(self, words: List[str]) -> int:
        """
        Interview explanation:
        A transformation cyclically shifts the even-index and odd-index
        subsequences independently. Two strings are equivalent iff those
        subsequences are rotations of each other. Groups = distinct
        canonical (min-rotation even, min-rotation odd) keys.

        Algorithm:
        - For each word, split even/odd chars; normalize each by Booth's
          least rotation; insert key into a set.
        - Answer is the set size.

        Complexity: O(total length) time, O(total length) space.
        """
        def least_rotation(s: str) -> str:
            if not s:
                return ""
            n = len(s)
            i = 0
            j = 1
            k = 0
            while i < n and j < n and k < n:
                diff = ord(s[(i + k) % n]) - ord(s[(j + k) % n])
                if diff == 0:
                    k += 1
                    continue
                if diff > 0:
                    i += k + 1
                else:
                    j += k + 1
                if i == j:
                    j += 1
                k = 0
            start = min(i, j)
            return s[start:] + s[:start]

        groups = set()
        for w in words:
            even = w[0::2]
            odd = w[1::2]
            groups.add(least_rotation(even) + "#" + least_rotation(odd))
        return len(groups)
# @lc code=end
