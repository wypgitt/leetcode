#
# @lc app=leetcode id=3316 lang=python3
#
# [3316] Find Maximum Removals From Source String
#
# https://leetcode.com/problems/find-maximum-removals-from-source-string/description/
#
# algorithms
# Medium (39.72%)
# Likes:    167
# Dislikes: 20
# Total Accepted:    12.6K
# Total Submissions: 31.6K
# Testcase Example:  "\"abbaa\"\n\"aba\"\n[0,1,2]"
#
#
# You are given a string source of size n, a string pattern that is a
# subsequence of source, and a sorted integer array targetIndices that
# contains distinct numbers in the range [0, n - 1].
#
# We define an operation as removing a character at an index idx from
# source such that:
#
# idx is an element of targetIndices.
#
# pattern remains a subsequence of source after removing the character.
#
# Performing an operation does not change the indices of the other
# characters in source. For example, if you remove 'c' from "acb", the
# character at index 2 would still be 'b'.
#
# Return the maximum number of operations that can be performed.
#
# Example 1:
#
# Input: source = "abbaa", pattern = "aba", targetIndices = [0,1,2]
#
# Output: 1
#
# Explanation:
#
# We can't remove source[0] but we can do either of these two operations:
#
# Remove source[1], so that source becomes "a_baa".
#
# Remove source[2], so that source becomes "ab_aa".
#
# Example 2:
#
# Input: source = "bcda", pattern = "d", targetIndices = [0,3]
#
# Output: 2
#
# Explanation:
#
# We can remove source[0] and source[3] in two operations.
#
# Example 3:
#
# Input: source = "dda", pattern = "dda", targetIndices = [0,1,2]
#
# Output: 0
#
# Explanation:
#
# We can't remove any character from source.
#
# Example 4:
#
# Input: source = "yeyeykyded", pattern = "yeyyd", targetIndices =
# [0,2,3,4]
#
# Output: 2
#
# Explanation:
#
# We can remove source[2] and source[3] in two operations.
#
# Constraints:
#
# 1 <= n == source.length <= 3 * 10^3
#
# 1 <= pattern.length <= n
#
# 1 <= targetIndices.length <= n
#
# targetIndices is sorted in ascending order.
#
# The input is generated such that targetIndices contains distinct
# elements in the range [0, n - 1].
#
# source and pattern consist only of lowercase English letters.
#
# The input is generated such that pattern appears as a subsequence in
# source.
#

# @lc code=start
from typing import List


class Solution:
    def maxRemovals(
        self, source: str, pattern: str, targetIndices: List[int]
    ) -> int:
        """
        Interview explanation:
        Maximize deletions of characters at targetIndices while pattern remains
        a subsequence of source (indices of non-deleted chars stay as labeled).

        Algorithm:
        - DP[i][j] = max removals using source[:i] after matching pattern[:j].
        - Transition: drop source[i] (+1 if removable), or match it to pattern[j].

        Complexity: O(n * m) time, O(n * m) space.
        """
        target = set(targetIndices)
        n, m = len(source), len(pattern)
        INF = -10**9
        dp = [[INF] * (m + 1) for _ in range(n + 1)]
        dp[0][0] = 0
        for i in range(n):
            for j in range(m + 1):
                if dp[i][j] <= INF // 2:
                    continue
                dp[i + 1][j] = max(
                    dp[i + 1][j], dp[i][j] + (1 if i in target else 0)
                )
                if j < m and source[i] == pattern[j]:
                    dp[i + 1][j + 1] = max(dp[i + 1][j + 1], dp[i][j])
        return dp[n][m]
# @lc code=end
