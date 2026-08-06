#
# @lc app=leetcode id=2840 lang=python3
#
# [2840] Check if Strings Can be Made Equal With Operations II
#
# https://leetcode.com/problems/check-if-strings-can-be-made-equal-with-operations-ii/description/
#
# algorithms
# Medium (74.11%)
# Likes:    580
# Dislikes: 18
# Total Accepted:    142.4K
# Total Submissions: 192.2K
# Testcase Example:  "\"abcdba\"\n\"cabdab\""
#
#
# You are given two strings s1 and s2, both of length n, consisting of
# lowercase English letters.
#
# You can apply the following operation on any of the two strings any
# number of times:
#
# Choose any two indices i and j such that i < j and the difference j - i
# is even, then swap the two characters at those indices in the string.
#
# Return true if you can make the strings s1 and s2 equal, and false
# otherwise.
#
# Example 1:
#
# Input: s1 = "abcdba", s2 = "cabdab"
# Output: true
# Explanation: We can apply the following operations on s1:
# - Choose the indices i = 0, j = 2. The resulting string is s1 =
# "cbadba".
# - Choose the indices i = 2, j = 4. The resulting string is s1 =
# "cbbdaa".
# - Choose the indices i = 1, j = 5. The resulting string is s1 = "cabdab"
# = s2.
#
# Example 2:
#
# Input: s1 = "abe", s2 = "bea"
# Output: false
# Explanation: It is not possible to make the two strings equal.
#
# Constraints:
#
# n == s1.length == s2.length
#
# 1 <= n <= 10^5
#
# s1 and s2 consist only of lowercase English letters.
#

# @lc code=start
from collections import Counter


class Solution:
    def checkStrings(self, s1: str, s2: str) -> bool:
        """
        Interview explanation:
        Can swap any two indices with even distance, so even positions form one
        freely permutable group and odd positions another.

        Algorithm:
        - Compare Counter of even indices and of odd indices between s1 and s2.

        Complexity: O(n) time, O(1) space (26 letters).
        """
        return Counter(s1[0::2]) == Counter(s2[0::2]) and Counter(s1[1::2]) == Counter(
            s2[1::2]
        )

    def checkStrings_sort(self, s1: str, s2: str) -> bool:
        """
        Interview explanation:
        Same parity-group idea via sorting each parity slice.

        Algorithm:
        - sorted(even1)==sorted(even2) and sorted(odd1)==sorted(odd2).

        Complexity: O(n log n) time, O(n) space.
        """
        return sorted(s1[0::2]) == sorted(s2[0::2]) and sorted(s1[1::2]) == sorted(
            s2[1::2]
        )
# @lc code=end
