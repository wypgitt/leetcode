#
# @lc app=leetcode id=1977 lang=python3
#
# [1977] Number of Ways to Separate Numbers
#
# https://leetcode.com/problems/number-of-ways-to-separate-numbers/description/
#
# algorithms
# Hard (21.73%)
# Likes:    541
# Dislikes: 61
# Total Accepted:    9.0K
# Total Submissions: 41.2K
# Testcase Example:  "\"327\""
#
# You wrote down many positive integers in a string called num. However, you
# realized that you forgot to add commas to seperate the different numbers. You
# remember that the list of integers was non-decreasing and that no integer had
# leading zeros.
#
# Return the number of possible lists of integers that you could have written
# down to get the string num. Since the answer may be large, return it modulo
# 10^9 + 7.
#
# Example 1:
#
# Input: num = "327"
# Output: 2
# Explanation: You could have written down the numbers:
# 3, 27
# 327
#
# Example 2:
#
# Input: num = "094"
# Output: 0
# Explanation: No numbers can have leading zeros and all numbers must be
# positive.
#
# Example 3:
#
# Input: num = "0"
# Output: 0
# Explanation: No numbers can have leading zeros and all numbers must be
# positive.
#
# Constraints:
#
# 1 <= num.length <= 3500
#
# num consists of digits '0' through '9'.
#

# @lc code=start
class Solution:
    def numberOfCombinations(self, num: str) -> int:
        """
        Interview explanation:
        Hard: count ways to split num into non-decreasing positive integers
        without leading zeros. DP with LCP for O(1)/O(n) comparisons.

        Algorithm:
        - dp[i][len] = ways ending a number of length `len` at index i-1.
        - Or: dp[i] = ways to split num[:i]; transition last number num[j:i]
          if no leading zero and >= previous number.
        - Precompute LCP table lcp[i][j] for comparing suffixes.

        Complexity: O(n^2) time, O(n^2) space.
        """
        MOD = 10**9 + 7
        n = len(num)
        if num[0] == "0":
            return 0

        # lcp[i][j] = common prefix length of num[i:] and num[j:]
        lcp = [[0] * (n + 1) for _ in range(n + 1)]
        for i in range(n - 1, -1, -1):
            for j in range(n - 1, -1, -1):
                if num[i] == num[j]:
                    lcp[i][j] = lcp[i + 1][j + 1] + 1

        def leq(a: int, b: int, length: int) -> bool:
            # num[a:a+length] <= num[b:b+length]
            common = lcp[a][b]
            if common >= length:
                return True
            return num[a + common] < num[b + common]

        # dp[i][j]: ways for prefix i using last number length j (ending at i)
        dp = [[0] * (n + 1) for _ in range(n + 1)]
        # pref[i][j] = sum dp[i][1..j]
        for i in range(1, n + 1):
            for j in range(1, i + 1):
                start = i - j
                if num[start] == "0":
                    dp[i][j] = 0
                elif start == 0:
                    dp[i][j] = 1
                else:
                    # previous number length k
                    # sum dp[start][k] for valid k
                    max_prev = start
                    # lengths k where previous number <= current
                    # if k < j: always ok if we take all shorter; if k==j need leq
                    # Use prefix sums carefully
                    s = 0
                    # all prev lengths < j (and <= start)
                    limit = min(j - 1, start)
                    for k in range(1, limit + 1):
                        s += dp[start][k]
                    if j <= start and leq(start - j, start, j):
                        s += dp[start][j]
                    dp[i][j] = s % MOD

        return sum(dp[n][j] for j in range(1, n + 1)) % MOD

    def numberOfCombinations_opt(self, num: str) -> int:
        """
        Interview explanation:
        Alternate optimized DP with prefix sums of ways by last length.

        Algorithm:
        - Same LCP comparisons; maintain prefix sums of dp[i][*] for O(n^2).

        Complexity: O(n^2) time, O(n^2) space.
        """
        MOD = 10**9 + 7
        n = len(num)
        if n == 0 or num[0] == "0":
            return 0
        lcp = [[0] * (n + 1) for _ in range(n + 1)]
        for i in range(n - 1, -1, -1):
            for j in range(n - 1, -1, -1):
                if num[i] == num[j]:
                    lcp[i][j] = lcp[i + 1][j + 1] + 1

        def ok_ge(prev_start: int, cur_start: int, length: int) -> bool:
            # previous num[prev_start:prev_start+length] <= current
            c = lcp[prev_start][cur_start]
            if c >= length:
                return True
            return num[prev_start + c] < num[cur_start + c]

        dp = [[0] * (n + 1) for _ in range(n + 1)]
        pref = [[0] * (n + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for j in range(1, i + 1):
                start = i - j
                if num[start] == "0":
                    dp[i][j] = 0
                elif start == 0:
                    dp[i][j] = 1
                else:
                    # sum dp[start][1..min(j-1,start)]
                    up = min(j - 1, start)
                    ways = pref[start][up]
                    if j <= start and ok_ge(start - j, start, j):
                        ways = (ways + dp[start][j]) % MOD
                    dp[i][j] = ways % MOD
            for j in range(1, n + 1):
                pref[i][j] = (pref[i][j - 1] + dp[i][j]) % MOD
        return pref[n][n]
# @lc code=end

