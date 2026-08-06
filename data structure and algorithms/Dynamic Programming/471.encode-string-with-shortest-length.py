#
# @lc app=leetcode id=471 lang=python3
#
# [471] Encode String with Shortest Length
#
# https://leetcode.com/problems/encode-string-with-shortest-length/description/
#
# algorithms
# Hard (50.57%)
# Likes:    633
# Dislikes: 54
# Total Accepted:    32.3K
# Total Submissions: 63.8K
# Testcase Example:  "\"aaa\""
#
#
# Given a string s, encode the string such that its encoded length is the
# shortest.
#
# The encoding rule is: k[encoded_string], where the encoded_string inside
# the square brackets is being repeated exactly k times. k should be a
# positive integer.
#
# If an encoding process does not make the string shorter, then do not
# encode it. If there are several solutions, return any of them.
#
# Example 1:
#
# Input: s = "aaa"
# Output: "aaa"
# Explanation: There is no way to encode it such that it is shorter than
# the input string, so we do not encode it.
#
# Example 2:
#
# Input: s = "aaaaa"
# Output: "5[a]"
# Explanation: "5[a]" is shorter than "aaaaa" by 1 character.
#
# Example 3:
#
# Input: s = "aaaaaaaaaa"
# Output: "10[a]"
# Explanation: "a9[a]" or "9[a]a" are also valid solutions, both of them
# have the same length = 5, which is the same as "10[a]".
#
# Constraints:
#
# 1 <= s.length <= 150
#
# s consists of only lowercase English letters.
#
# @lc code=start
class Solution:
    def encode(self, s: str) -> str:
        """
        Interview explanation:
        Premium DP. dp[i][j] = shortest encoding of s[i:j+1]. Try every split
        and also detect repeated pattern: if s[i:j+1] = pattern * k, encode as
        k[encode(pattern)]. Keep the shortest among raw, split, and repeat forms.

        Algorithm:
        - n = len(s); dp[i][j] init to s[i:j+1].
        - For length L = 1..n, for each i, j = i+L-1:
          - Try splits: dp[i][k] + dp[k+1][j]
          - Repeat: t = s[i:j+1]; in (t+t).find(t,1) gives period; if divides,
            candidate = str(count) + '[' + dp[i][i+period-1] + ']'
          - Take min length string.

        Complexity: O(n^3) time (with string ops), O(n^2) space.
        """
        n = len(s)
        if n <= 1:
            return s
        dp = [[""] * n for _ in range(n)]

        for length in range(1, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                substr = s[i : j + 1]
                dp[i][j] = substr
                if length > 4:
                    for k in range(i, j):
                        cand = dp[i][k] + dp[k + 1][j]
                        if len(cand) < len(dp[i][j]):
                            dp[i][j] = cand
                    # find shortest pattern repeat
                    doubled = substr + substr
                    pos = doubled.find(substr, 1)
                    if pos < length:
                        period = pos
                        if length % period == 0:
                            count = length // period
                            cand = f"{count}[{dp[i][i + period - 1]}]"
                            if len(cand) < len(dp[i][j]):
                                dp[i][j] = cand
        return dp[0][n - 1]
# @lc code=end
