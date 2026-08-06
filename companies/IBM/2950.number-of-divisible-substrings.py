#
# @lc app=leetcode id=2950 lang=python3
#
# [2950] Number of Divisible Substrings
#
# https://leetcode.com/problems/number-of-divisible-substrings/description/
#
# algorithms
# Medium (74.73%)
# Likes:    31
# Dislikes: 6
# Total Accepted:    3.8K
# Total Submissions: 5.1K
# Testcase Example:  "\"asdf\""
#
#
# Each character of the English alphabet has been mapped to a digit as
# shown below.
#
# A string is divisible if the sum of the mapped values of its characters
# is divisible by its length.
#
# Given a string s, return the number of divisible substrings of s.
#
# A substring is a contiguous non-empty sequence of characters within a
# string.
#
# Example 1:
#
#                         Substring
#                         Mapped
#                         Sum
#                         Length
#                         Divisible?
#
#                         a
#                         1
#                         1
#                         1
#                         Yes
#
#                         s
#                         7
#                         7
#                         1
#                         Yes
#
#                         d
#                         2
#                         2
#                         1
#                         Yes
#
#                         f
#                         3
#                         3
#                         1
#                         Yes
#
#                         as
#                         1, 7
#                         8
#                         2
#                         Yes
#
#                         sd
#                         7, 2
#                         9
#                         2
#                         No
#
#                         df
#                         2, 3
#                         5
#                         2
#                         No
#
#                         asd
#                         1, 7, 2
#                         10
#                         3
#                         No
#
#                         sdf
#                         7, 2, 3
#                         12
#                         3
#                         Yes
#
#                         asdf
#                         1, 7, 2, 3
#                         13
#                         4
#                         No
#
# Input: word = "asdf"
# Output: 6
# Explanation: The table above contains the details about every substring
# of word, and we can see that 6 of them are divisible.
#
# Example 2:
#
# Input: word = "bdh"
# Output: 4
# Explanation: The 4 divisible substrings are: "b", "d", "h", "bdh".
# It can be shown that there are no other substrings of word that are
# divisible.
#
# Example 3:
#
# Input: word = "abcd"
# Output: 6
# Explanation: The 6 divisible substrings are: "a", "b", "c", "d", "ab",
# "cd".
# It can be shown that there are no other substrings of word that are
# divisible.
#
# Constraints:
#
# 1 <= word.length <= 2000
#
# word consists only of lowercase English letters.
#
# @lc code=start
from collections import defaultdict


class Solution:
    def countDivisibleSubstrings(self, word: str) -> int:
        """
        Interview explanation:
        Premium: map letters to digits (ab->1, cde->2, ..., xyz->9). Count
        substrings whose mapped-sum is divisible by their length.

        Algorithm:
        - Average of values in [1,9] must be integer avg. For each avg,
          transform a_i' = a_i - avg; count subarrays with sum 0 via prefix
          frequency map.

        Complexity: O(n) time (9 passes), O(n) space.
        """
        groups = ["ab", "cde", "fgh", "ijk", "lmn", "opq", "rst", "uvw", "xyz"]
        mp = {}
        for i, g in enumerate(groups, 1):
            for c in g:
                mp[c] = i
        ans = 0
        for avg in range(1, 10):
            cnt = defaultdict(int)
            cnt[0] = 1
            pref = 0
            for c in word:
                pref += mp[c] - avg
                ans += cnt[pref]
                cnt[pref] += 1
        return ans

    def countDivisibleSubstrings_brute(self, word: str) -> int:
        """
        Interview explanation:
        Alternate O(n^2) enumeration with running mapped sum.

        Algorithm:
        - For each start, extend end; check sum % length == 0.

        Complexity: O(n^2) time, O(1) space.
        """
        groups = ["ab", "cde", "fgh", "ijk", "lmn", "opq", "rst", "uvw", "xyz"]
        mp = {}
        for i, g in enumerate(groups, 1):
            for c in g:
                mp[c] = i
        ans = 0
        n = len(word)
        for i in range(n):
            s = 0
            for j in range(i, n):
                s += mp[word[j]]
                if s % (j - i + 1) == 0:
                    ans += 1
        return ans
# @lc code=end

