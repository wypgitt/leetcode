#
# @lc app=leetcode id=2430 lang=python3
#
# [2430] Maximum Deletions on a String
#
# https://leetcode.com/problems/maximum-deletions-on-a-string/description/
#
# algorithms
# Hard (36.15%)
# Likes:    525
# Dislikes: 61
# Total Accepted:    18K
# Total Submissions: 49.7K
# Testcase Example:  "\"abcabcdabc\""
#
# You are given a string s consisting of only lowercase English letters. In one
# operation, you can:
#
#
# Delete the entire string s, or
#
#
# Delete the first i letters of s if the first i letters of s are equal to the
# following i letters in s, for any i in the range 1 <= i <= s.length / 2.
#
# For example, if s = "ababc", then in one operation, you could delete the first
# two letters of s to get "abc", since the first two letters of s and the
# following two letters of s are both equal to "ab".
#
# Return the maximum number of operations needed to delete all of s.
#
#
#
# Example 1:
#
# Input: s = "abcabcdabc"
# Output: 2
# Explanation:
# - Delete the first 3 letters ("abc") since the next 3 letters are equal. Now,
# s = "abcdabc".
# - Delete all the letters.
# We used 2 operations so return 2. It can be proven that 2 is the maximum
# number of operations needed.
# Note that in the second operation we cannot delete "abc" again because the
# next occurrence of "abc" does not happen in the next 3 letters.
#
# Example 2:
#
# Input: s = "aaabaab"
# Output: 4
# Explanation:
# - Delete the first letter ("a") since the next letter is equal. Now, s =
# "aabaab".
# - Delete the first 3 letters ("aab") since the next 3 letters are equal. Now,
# s = "aab".
# - Delete the first letter ("a") since the next letter is equal. Now, s = "ab".
# - Delete all the letters.
# We used 4 operations so return 4. It can be proven that 4 is the maximum
# number of operations needed.
#
# Example 3:
#
# Input: s = "aaaaa"
# Output: 5
# Explanation: In each operation, we can delete the first letter of s.
#
#
#
# Constraints:
#
#
# 1 <= s.length <= 4000
#
#
# s consists only of lowercase English letters.
#

# @lc code=start
from functools import cache


class Solution:
    def deleteString(self, s: str) -> int:
        """
        Interview explanation:
        In one op delete a non-empty prefix that equals the following substring of
        same length. Maximize number of operations to delete whole string.

        Algorithm:
        - DP with LCP table: if lcp[i][i+l]>=l then dp[i]=max(1+dp[i+l]).

        Complexity: O(n^2) time/space.
        """
        n = len(s)
        lcp = [[0] * (n + 1) for _ in range(n + 1)]
        for i in range(n - 1, -1, -1):
            for j in range(n - 1, -1, -1):
                if s[i] == s[j]:
                    lcp[i][j] = lcp[i + 1][j + 1] + 1
        dp = [1] * n
        for i in range(n - 1, -1, -1):
            for length in range(1, (n - i) // 2 + 1):
                if lcp[i][i + length] >= length:
                    dp[i] = max(dp[i], 1 + dp[i + length])
        return dp[0]

    def deleteString_dp(self, s: str) -> int:
        """
        Interview explanation:
        Alternate memoized recursion with direct string equality.

        Algorithm:
        - dfs(i) tries all valid prefix lengths.

        Complexity: O(n^3) time with slicing, O(n) space.
        """
        n = len(s)

        @cache
        def dfs(i: int) -> int:
            ans = 1
            for length in range(1, (n - i) // 2 + 1):
                if s[i : i + length] == s[i + length : i + 2 * length]:
                    ans = max(ans, 1 + dfs(i + length))
            return ans

        return dfs(0)
# @lc code=end
