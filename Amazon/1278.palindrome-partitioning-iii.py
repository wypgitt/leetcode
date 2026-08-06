#
# @lc app=leetcode id=1278 lang=python3
#
# [1278] Palindrome Partitioning III
#
# https://leetcode.com/problems/palindrome-partitioning-iii/description/
#
# algorithms
# Hard (62.31%)
# Likes:    1223
# Dislikes: 19
# Total Accepted:    40.2K
# Total Submissions: 64.5K
# Testcase Example:  "\"abc\""
#
# You are given a string s containing lowercase letters and an integer k. You
# need to :
#
# First, change some characters of s to other lowercase English letters.
#
# Then divide s into k non-empty disjoint substrings such that each substring
# is a palindrome.
#
# Return the minimal number of characters that you need to change to divide the
# string.
#
# Example 1:
#
# Input: s = "abc", k = 2
# Output: 1
# Explanation: You can split the string into "ab" and "c", and change 1
# character in "ab" to make it palindrome.
#
# Example 2:
#
# Input: s = "aabbc", k = 3
# Output: 0
# Explanation: You can split the string into "aa", "bb" and "c", all of them
# are palindrome.
#
# Example 3:
#
# Input: s = "leetcode", k = 8
# Output: 0
#
# Constraints:
#
# 1 <= k <= s.length <= 100.
#
# s only contains lowercase English letters.
#

# @lc code=start

class Solution:
    def palindromePartition(self, s: str, k: int) -> int:
        """
        Interview explanation:
        Split s into k substrings minimizing total changes to make each a
        palindrome. Precompute cost(i,j)=changes for s[i..j]; DP:
        dp[i][p]=min cost to split s[:i] into p parts.

        Algorithm:
        - n=len(s); cost[i][j] via expand or two pointers.
        - dp[0][0]=0; INF else; for parts 1..k, for end, for mid: minimize
          dp[mid][parts-1]+cost[mid][end-1].
        - Return dp[n][k].

        Complexity: O(n^2 * k) time, O(n^2) space.
        """
        n = len(s)
        cost = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                c = 0
                l, r = i, j
                while l < r:
                    if s[l] != s[r]:
                        c += 1
                    l += 1
                    r -= 1
                cost[i][j] = c

        INF = 10**9
        dp = [[INF] * (k + 1) for _ in range(n + 1)]
        dp[0][0] = 0
        for parts in range(1, k + 1):
            for end in range(parts, n + 1):
                for mid in range(parts - 1, end):
                    dp[end][parts] = min(
                        dp[end][parts], dp[mid][parts - 1] + cost[mid][end - 1]
                    )
        return dp[n][k]
# @lc code=end
