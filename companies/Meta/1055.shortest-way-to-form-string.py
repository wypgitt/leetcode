#
# @lc app=leetcode id=1055 lang=python3
#
# [1055] Shortest Way to Form String
#
# https://leetcode.com/problems/shortest-way-to-form-string/description/
#
# algorithms
# Medium (61.74%)
# Likes:    1340
# Dislikes: 77
# Total Accepted:    114K
# Total Submissions: 184.6K
# Testcase Example:  "\"abc\"\n\"abcbc\""
#
#
# A subsequence of a string is a new string that is formed from the
# original string by deleting some (can be none) of the characters without
# disturbing the relative positions of the remaining characters. (i.e.,
# "ace" is a subsequence of "abcde" while "aec" is not).
#
# Given two strings source and target, return the minimum number of
# subsequences of source such that their concatenation equals target. If
# the task is impossible, return -1.
#
# Example 1:
#
# Input: source = "abc", target = "abcbc"
# Output: 2
# Explanation: The target "abcbc" can be formed by "abc" and "bc", which
# are subsequences of source "abc".
#
# Example 2:
#
# Input: source = "abc", target = "acdbc"
# Output: -1
# Explanation: The target string cannot be constructed from the
# subsequences of source string due to the character "d" in target string.
#
# Example 3:
#
# Input: source = "xyz", target = "xzyxz"
# Output: 3
# Explanation: The target string can be constructed as follows "xz" + "y"
# + "xz".
#
# Constraints:
#
# 1 <= source.length, target.length <= 1000
#
# source and target consist of lowercase English letters.
#
# @lc code=start
from typing import List


class Solution:
    def shortestWay(self, source: str, target: str) -> int:
        """
        Interview explanation:
        Premium. Form target as concatenation of subsequences of source. Greedy:
        repeatedly scan source matching as much of remaining target as possible;
        each full pass that advances counts as one subsequence. Impossible if a
        char in target never appears in source.

        Algorithm:
        - source_set check; i=0 over target; ans=0
        - While i<len(target): j over source matching target[i]; if no progress -1; ans++

        Complexity: O(|source| * |target|) time, O(1) alphabet space.
        """
        src = set(source)
        for ch in target:
            if ch not in src:
                return -1
        i = 0
        ans = 0
        m = len(target)
        while i < m:
            for ch in source:
                if i < m and ch == target[i]:
                    i += 1
            ans += 1
        return ans

    def shortestWay_binary_search(self, source: str, target: str) -> int:
        """
        Interview explanation:
        Alternate: index lists per char in source; for each target char
        binary-search next occurrence after current position; reset when stuck.

        Algorithm:
        - Map char→sorted indices; walk target with pos in source; ans++ on wrap

        Complexity: O(|target| log |source|) time, O(|source|) space.
        """
        from collections import defaultdict
        import bisect

        pos = defaultdict(list)
        for i, ch in enumerate(source):
            pos[ch].append(i)
        ans = 1
        cur = -1
        for ch in target:
            if ch not in pos:
                return -1
            idxs = pos[ch]
            j = bisect.bisect_right(idxs, cur)
            if j == len(idxs):
                ans += 1
                cur = idxs[0]
            else:
                cur = idxs[j]
        return ans
# @lc code=end
