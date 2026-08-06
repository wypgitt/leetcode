#
# @lc app=leetcode id=3998 lang=python3
#
# [3998] Transform Binary String Using Subsequence Sort
#
# https://leetcode.com/problems/transform-binary-string-using-subsequence-sort/description/
#
# algorithms
# Medium (37.86%)
# Likes:    66
# Dislikes: 6
# Total Accepted:    13.8K
# Total Submissions: 36.6K
# Testcase Example:  "\"101\"\n[\"1?1\",\"0?1\",\"0?0\"]"
#
#
# You are given a binary string s.
#
# You are also given an array of strings strs, where each strs[i] has the
# same length as s and consists of characters '0', '1', and '?'. Each '?'
# can be replaced by either '0' or '1'.
#
# You may perform the following operation any number of times (including
# zero):
#
# Choose any subsequence sub of s.
#
# Sort sub in non-decreasing order.
#
# Replace the chosen subsequence in s with the sorted sub, keeping all
# other characters unchanged.
#
# Return a boolean array ans, where ans[i] is true if it's possible to
# replace all '?' in strs[i] with '0' or '1' and transform s into the
# resulting string using the allowed operation above, otherwise return
# false.
#
# Example 1:
#
# Input: s = "101", strs = ["1?1","0?1","0?0"]
#
# Output: [true,true,false]
#
# Explanation:
#
#                         i
#                         strs[i]
#                         Replacement
#                         Result strs[i]
#                         Operation(s)
#                         Result
#
#                         0
#                         "1?1"
#                         ? → 0
#                         "101"
#                         Matches s.
#                         true
#
#                         1
#                         "0?1"
#                         ? → 1
#                         "011"
#                         Select the subsequence at indices [0..2] of s →
# "101".
#
#                         Sort "101" to get "011" = strs[i].
#                         true
#
#                         2
#                         "0?0"
#                         ? → 0 or 1
#                         "000" or "010"
#                         Not feasible.
#                         false
#
# Thus, ans = [true, true, false].
#
# Example 2:
#
# Input: s = "1100", strs = ["0011","11?1","1?1?"]
#
# Output: [true,false,true]
#
# Explanation:
#
#                         i
#                         strs[i]
#                         Replacement
#                         Result strs[i]
#                         Operation(s)
#                         Result
#
#                         0
#                         "0011"
#                         -
#                         "0011"
#                         Select the subsequence at indices [0..3] of s →
# "1100".
#
#                         Sort "1100" to get "0011" = strs[i].
#                         true
#
#                         1
#                         "11?1"
#                         ? → 0
#                         "1101"
#                         Not feasible.
#                         false
#
#                         2
#                         "1?1?"
#                         First ? → 0
#
#                         Second ? → 0
#                         "1010"
#                         Select the subsequence at indices [1, 2] of s →
# "10".
#
#                         Sort "10" to get "01", so s = "1010".
#                         true
#
# Thus, ans = [true, false, true].
#
# Example 3:
#
# Input: s = "1010", strs = ["0011"]
#
# Output: [true]
#
# Explanation:
#
#                         i
#                         strs[i]
#                         Replacement
#                         Result strs[i]
#                         Operation(s)
#                         Result
#
#                         0
#                         "0011"
#                         -
#                         "0011"
#                         Select the subsequence at indices [0, 2, 3] of s
# → "110".
#
#                         Sort "110" to get "011", so s = "0011" =
# strs[i].
#                         true
#
# Thus, ans = [true].
#
# Constraints:
#
# 1 <= n == s.length <= 2000
#
# s[i] is either '0' or '1'.
#
# 1 <= strs.length <= 2000
#
# strs[i].length == n
#
# strs[i] is either '0', '1', or '?'​​​​​​​.
#

# @lc code=start
from typing import List


class Solution:
    def transformStr(self, s: str, strs: List[str]) -> List[bool]:
        """
        Interview explanation:
        Sorting a binary subsequence only moves 0s left / 1s right. Reachable
        targets t with the same # of 0s satisfy: for every prefix,
        count0(t) >= count0(s). With '?', place 0s as left as possible.

        Algorithm:
        - For each pattern: need0 = zeros(s) - fixed zeros in pattern; must
          lie in [0, #?].
        - Greedily assign '?' -> '0' while need0 > 0 (leftmost); reject if any
          prefix has fewer 0s than s.

        Complexity: O(|strs| * n) time, O(1) extra space.
        """
        n = len(s)
        zeros_s = s.count("0")
        pref0 = [0] * (n + 1)
        for i, ch in enumerate(s):
            pref0[i + 1] = pref0[i] + (ch == "0")

        def ok(pat: str) -> bool:
            need0 = zeros_s - pat.count("0")
            q = pat.count("?")
            if need0 < 0 or need0 > q:
                return False
            c0 = 0
            for i, ch in enumerate(pat):
                if ch == "0":
                    c0 += 1
                elif ch == "?":
                    if need0 > 0:
                        c0 += 1
                        need0 -= 1
                if c0 < pref0[i + 1]:
                    return False
            return need0 == 0

        return [ok(p) for p in strs]
# @lc code=end
