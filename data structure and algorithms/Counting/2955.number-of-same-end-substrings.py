#
# @lc app=leetcode id=2955 lang=python3
#
# [2955] Number of Same-End Substrings
#
# https://leetcode.com/problems/number-of-same-end-substrings/description/
#
# algorithms
# Medium (61.73%)
# Likes:    86
# Dislikes: 18
# Total Accepted:    9.1K
# Total Submissions: 14.7K
# Testcase Example:  "\"abcaab\"\n[[0,0],[1,4],[2,5],[0,5]]"
#
#
# You are given a 0-indexed string s, and a 2D array of integers queries,
# where queries[i] = [l_i, r_i] indicates a substring of s starting from
# the index l_i and ending at the index r_i (both inclusive), i.e.
# s[l_i..r_i].
#
# Return an array ans where ans[i] is the number of same-end substrings of
# queries[i].
#
# A 0-indexed string t of length n is called same-end if it has the same
# character at both of its ends, i.e., t[0] == t[n - 1].
#
# A substring is a contiguous non-empty sequence of characters within a
# string.
#
# Example 1:
#
# Input: s = "abcaab", queries = [[0,0],[1,4],[2,5],[0,5]]
# Output: [1,5,5,10]
# Explanation: Here is the same-end substrings of each query:
# 1^st query: s[0..0] is "a" which has 1 same-end substring: "a".
# 2^nd query: s[1..4] is "bcaa" which has 5 same-end substrings: "bcaa",
# "bcaa", "bcaa", "bcaa", "bcaa".
# 3^rd query: s[2..5] is "caab" which has 5 same-end substrings: "caab",
# "caab", "caab", "caab", "caab".
# 4^th query: s[0..5] is "abcaab" which has 10 same-end substrings:
# "abcaab", "abcaab", "abcaab", "abcaab", "abcaab", "abcaab", "abcaab",
# "abcaab", "abcaab", "abcaab".
#
# Example 2:
#
# Input: s = "abcd", queries = [[0,3]]
# Output: [4]
# Explanation: The only query is s[0..3] which is "abcd". It has 4
# same-end substrings: "abcd", "abcd", "abcd", "abcd".
#
# Constraints:
#
# 2 <= s.length <= 3 * 10^4
#
# s consists only of lowercase English letters.
#
# 1 <= queries.length <= 3 * 10^4
#
# queries[i] = [l_i, r_i]
#
# 0 <= l_i <= r_i < s.length
#
# @lc code=start
from typing import List


class Solution:
    def sameEndSubstringCount(self, s: str, queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Premium: same-end substring has equal first/last char. For each query
        [l,r], count such substrings inside s[l..r].

        Algorithm:
        - Prefix counts of each letter. For freq x of a letter in range,
          contribute C(x,2)+x = x*(x+1)/2 (pairs of ends plus singletons).

        Complexity: O((n+q)*26) time, O(26n) space.
        """
        n = len(s)
        pref = [[0] * 26 for _ in range(n + 1)]
        for i, ch in enumerate(s, 1):
            pref[i] = pref[i - 1][:]
            pref[i][ord(ch) - 97] += 1
        ans = []
        for l, r in queries:
            total = 0
            for c in range(26):
                x = pref[r + 1][c] - pref[l][c]
                total += x * (x + 1) // 2
            ans.append(total)
        return ans
# @lc code=end

