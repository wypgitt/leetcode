#
# @lc app=leetcode id=3579 lang=python3
#
# [3579] Minimum Steps to Convert String with Operations
#
# https://leetcode.com/problems/minimum-steps-to-convert-string-with-operations/description/
#
# algorithms
# Hard (43.54%)
# Likes:    47
# Dislikes: 4
# Total Accepted:    4.6K
# Total Submissions: 10.6K
# Testcase Example:  "\"abcdf\"\n\"dacbe\""
#
#
# You are given two strings, word1 and word2, of equal length. You need to
# transform word1 into word2.
#
# For this, divide word1 into one or more contiguous substrings. For each
# substring substr you can perform the following operations:
#
# Replace: Replace the character at any one index of substr with another
# lowercase English letter.
#
# Swap: Swap any two characters in substr.
#
# Reverse Substring: Reverse substr.
#
# Each of these counts as one operation and each character of each
# substring can be used in each type of operation at most once (i.e. no
# single index may be involved in more than one replace, one swap, or one
# reverse).
#
# Return the minimum number of operations required to transform word1 into
# word2.
#
# Example 1:
#
# Input: word1 = "abcdf", word2 = "dacbe"
#
# Output: 4
#
# Explanation:
#
# Divide word1 into "ab", "c", and "df". The operations are:
#
# For the substring "ab",
#
# Perform operation of type 3 on "ab" -> "ba".
#
# Perform operation of type 1 on "ba" -> "da".
#
# For the substring "c" do no operations.
#
# For the substring "df",
#
# Perform operation of type 1 on "df" -> "bf".
#
# Perform operation of type 1 on "bf" -> "be".
#
# Example 2:
#
# Input: word1 = "abceded", word2 = "baecfef"
#
# Output: 4
#
# Explanation:
#
# Divide word1 into "ab", "ce", and "ded". The operations are:
#
# For the substring "ab",
#
# Perform operation of type 2 on "ab" -> "ba".
#
# For the substring "ce",
#
# Perform operation of type 2 on "ce" -> "ec".
#
# For the substring "ded",
#
# Perform operation of type 1 on "ded" -> "fed".
#
# Perform operation of type 1 on "fed" -> "fef".
#
# Example 3:
#
# Input: word1 = "abcdef", word2 = "fedabc"
#
# Output: 2
#
# Explanation:
#
# Divide word1 into "abcdef". The operations are:
#
# For the substring "abcdef",
#
# Perform operation of type 3 on "abcdef" -> "fedcba".
#
# Perform operation of type 2 on "fedcba" -> "fedabc".
#
# Constraints:
#
# 1 <= word1.length == word2.length <= 100
#
# word1 and word2 consist only of lowercase English letters.
#

# @lc code=start

from collections import Counter
from math import inf


class Solution:
    def minOperations(self, word1: str, word2: str) -> int:
        """
        Interview explanation:
        Partition into contiguous segments; each segment may optionally reverse
        once, then fix mismatches with swaps (pair inverse mismatches) and
        replacements. Partition DP chooses cut points.

        Algorithm:
        - calc(l,r,rev): scan aligned pairs; unmatched (a→b) cancels with (b→a)
          via one swap, else counts as a replace.
        - f[i] = min over j<i of f[j] + min(calc(j,i-1,False),
          1+calc(j,i-1,True)).

        Complexity: O(n^3) time, O(n) space.
        """
        def calc(l: int, r: int, rev: bool) -> int:
            cnt: Counter = Counter()
            res = 0
            for i in range(l, r + 1):
                j = r - (i - l) if rev else i
                a, b = word1[j], word2[i]
                if a != b:
                    if cnt[(b, a)] > 0:
                        cnt[(b, a)] -= 1
                    else:
                        cnt[(a, b)] += 1
                        res += 1
            return res

        n = len(word1)
        f = [inf] * (n + 1)
        f[0] = 0
        for i in range(1, n + 1):
            for j in range(i):
                t = min(calc(j, i - 1, False), 1 + calc(j, i - 1, True))
                if f[j] + t < f[i]:
                    f[i] = f[j] + t
        return int(f[n])
# @lc code=end
