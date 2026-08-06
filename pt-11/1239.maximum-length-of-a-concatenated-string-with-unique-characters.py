#
# @lc app=leetcode id=1239 lang=python3
#
# [1239] Maximum Length of a Concatenated String with Unique Characters
#
# https://leetcode.com/problems/maximum-length-of-a-concatenated-string-with-unique-characters/description/
#
# algorithms
# Medium (54.87%)
# Likes:    4593
# Dislikes: 340
# Total Accepted:    330K
# Total Submissions: 602K
# Testcase Example:  "[\"un\",\"iq\",\"ue\"]"
#
# You are given an array of strings arr. A string s is formed by the
# concatenation of a subsequence of arr that has unique characters.
#
# Return the maximum possible length of s.
#
# A subsequence is an array that can be derived from another array by deleting
# some or no elements without changing the order of the remaining elements.
#
# Example 1:
#
# Input: arr = ["un","iq","ue"]
# Output: 4
# Explanation: All the valid concatenations are:
# - ""
# - "un"
# - "iq"
# - "ue"
# - "uniq" ("un" + "iq")
# - "ique" ("iq" + "ue")
# Maximum length is 4.
#
# Example 2:
#
# Input: arr = ["cha","r","act","ers"]
# Output: 6
# Explanation: Possible longest valid concatenations are "chaers" ("cha" +
# "ers") and "acters" ("act" + "ers").
#
# Example 3:
#
# Input: arr = ["abcdefghijklmnopqrstuvwxyz"]
# Output: 26
# Explanation: The only string in arr has all 26 characters.
#
# Constraints:
#
# 1 <= arr.length <= 16
#
# 1 <= arr[i].length <= 26
#
# arr[i] contains only lowercase English letters.
#


# @lc code=start
from typing import List

class Solution:
    def maxLength(self, arr: List[str]) -> int:
        """
        Interview explanation:
        Max length of concatenation of subset of strings with all unique chars.
        Backtrack with bitmasks; skip strings with internal duplicates.

        Algorithm:
        - Convert each valid string to bitmask; DFS take/skip; track max bit count

        Complexity: O(2^m) for m valid strings.
        """
        masks = []
        for s in arr:
            m = 0
            ok = True
            for ch in s:
                bit = 1 << (ord(ch) - 97)
                if m & bit:
                    ok = False
                    break
                m |= bit
            if ok:
                masks.append(m)

        ans = 0

        def dfs(i: int, cur: int) -> None:
            nonlocal ans
            ans = max(ans, cur.bit_count())
            for j in range(i, len(masks)):
                if cur & masks[j] == 0:
                    dfs(j + 1, cur | masks[j])

        dfs(0, 0)
        return ans

    def maxLength_dp(self, arr: List[str]) -> int:
        """
        Interview explanation:
        Alternate iterative DP: set of achievable masks; try adding each string.

        Algorithm:
        - dp={0}; for each mask try combine with existing; keep max popcount

        Complexity: O(2^m) states.
        """
        dp = {0}
        best = 0
        for s in arr:
            m = 0
            ok = True
            for ch in s:
                bit = 1 << (ord(ch) - 97)
                if m & bit:
                    ok = False
                    break
                m |= bit
            if not ok:
                continue
            for prev in list(dp):
                if prev & m == 0:
                    nxt = prev | m
                    dp.add(nxt)
                    best = max(best, nxt.bit_count())
        return best
# @lc code=end
