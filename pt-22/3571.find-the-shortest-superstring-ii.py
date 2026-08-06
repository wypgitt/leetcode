#
# @lc app=leetcode id=3571 lang=python3
#
# [3571] Find the Shortest Superstring II
#
# https://leetcode.com/problems/find-the-shortest-superstring-ii/description/
#
# algorithms
# Easy (48.44%)
# Likes:    8
# Dislikes: 2
# Total Accepted:    868
# Total Submissions: 1.8K
# Testcase Example:  "\"aba\"\n\"bab\""
#
#
# You are given two strings, s1 and s2. Return the shortest possible
# string that contains both s1 and s2 as substrings. If there are multiple
# valid answers, return any one of them.
#
# A substring is a contiguous sequence of characters within a string.
#
# Example 1:
#
# Input: s1 = "aba", s2 = "bab"
#
# Output: "abab"
#
# Explanation:
#
# "abab" is the shortest string that contains both "aba" and "bab" as
# substrings.
#
# Example 2:
#
# Input: s1 = "aa", s2 = "aaa"
#
# Output: "aaa"
#
# Explanation:
#
# "aa" is already contained within "aaa", so the shortest superstring is
# "aaa".
#
# Constraints:
#
# 1 <= s1.length <= 100
#
# 1 <= s2.length <= 100
#
# s1 and s2 consist of lowercase English letters only.
#

# @lc code=start

class Solution:
    def shortestSuperstring(self, s1: str, s2: str) -> str:
        """
        Interview explanation:
        Shortest string containing both as substrings is either one string (if it
        already contains the other) or the best overlap merge of the two orders.

        Algorithm:
        - If s1 in s2 return s2; if s2 in s1 return s1.
        - Max overlap: longest suffix of A that is a prefix of B; merge both
          (s1 then s2) and (s2 then s1); take the shorter.

        Complexity: O(n^2) time, O(n) space (n = |s1|+|s2|).
        """
        if s1 in s2:
            return s2
        if s2 in s1:
            return s1

        def merge(a: str, b: str) -> str:
            max_ov = 0
            lim = min(len(a), len(b))
            for ov in range(1, lim + 1):
                if a[-ov:] == b[:ov]:
                    max_ov = ov
            return a + b[max_ov:]

        m1 = merge(s1, s2)
        m2 = merge(s2, s1)
        return m1 if len(m1) <= len(m2) else m2
# @lc code=end
