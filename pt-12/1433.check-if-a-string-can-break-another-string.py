#
# @lc app=leetcode id=1433 lang=python3
#
# [1433] Check If a String Can Break Another String
#
# https://leetcode.com/problems/check-if-a-string-can-break-another-string/description/
#
# algorithms
# Medium (71.15%)
# Likes:    788
# Dislikes: 156
# Total Accepted:    55.6K
# Total Submissions: 78.1K
# Testcase Example:  "\"abc\""
#
# Given two strings: s1 and s2 with the same size, check if some permutation of
# string s1 can break some permutation of string s2 or vice-versa. In other
# words s2 can break s1 or vice-versa.
#
# A string x can break string y (both of size n) if x[i] >= y[i] (in
# alphabetical order) for all i between 0 and n-1.
#
# Example 1:
#
# Input: s1 = "abc", s2 = "xya"
# Output: true
# Explanation: "ayx" is a permutation of s2="xya" which can break to string
# "abc" which is a permutation of s1="abc".
#
# Example 2:
#
# Input: s1 = "abe", s2 = "acd"
# Output: false
# Explanation: All permutations for s1="abe" are: "abe", "aeb", "bae", "bea",
# "eab" and "eba" and all permutation for s2="acd" are: "acd", "adc", "cad",
# "cda", "dac" and "dca". However, there is not any permutation from s1 which
# can break some permutation from s2 and vice-versa.
#
# Example 3:
#
# Input: s1 = "leetcodee", s2 = "interview"
# Output: true
#
# Constraints:
#
# s1.length == n
#
# s2.length == n
#
# 1 <= n <= 10^5
#
# All strings consist of lowercase English letters.
#

# @lc code=start
class Solution:
    def checkIfCanBreak(self, s1: str, s2: str) -> bool:
        """
        Interview explanation:
        s1 can break s2 if some permutation has every char >= corresponding in
        s2. Sort both; check a[i]>=b[i] for all i (or vice versa).

        Algorithm:
        (sort)
        - a,b = sorted(s1), sorted(s2); return all >= or all <=.

        Complexity: O(n log n) time, O(n) space.
        """
        a = sorted(s1)
        b = sorted(s2)
        return all(x >= y for x, y in zip(a, b)) or all(x <= y for x, y in zip(a, b))

    def checkIfCanBreak_count(self, s1: str, s2: str) -> bool:
        """
        Interview explanation:
        Alternate counting sort on 26 letters; compare cumulative / pairwise
        in sorted order without general sort.

        Algorithm:
        - Count freqs; expand to sorted arrays via counts; same compare.

        Complexity: O(n) time, O(1) extra (26).
        """
        def counts(s):
            c = [0] * 26
            for ch in s:
                c[ord(ch) - 97] += 1
            return c

        def can(c1, c2):
            # merge like sorted compare using two pointers on alphabet
            i = j = 0
            rem1 = rem2 = 0
            # simpler: build sorted via counts
            a, b = [], []
            for ch in range(26):
                a.extend([chr(97 + ch)] * c1[ch])
                b.extend([chr(97 + ch)] * c2[ch])
            return all(x >= y for x, y in zip(a, b))

        c1, c2 = counts(s1), counts(s2)
        return can(c1, c2) or can(c2, c1)
# @lc code=end
