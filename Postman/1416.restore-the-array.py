#
# @lc app=leetcode id=1416 lang=python3
#
# [1416] Restore The Array
#
# https://leetcode.com/problems/restore-the-array/description/
#
# algorithms
# Hard (46.74%)
# Likes:    1681
# Dislikes: 53
# Total Accepted:    69.7K
# Total Submissions: 149K
# Testcase Example:  "\"1000\""
#
# A program was supposed to print an array of integers. The program forgot to
# print whitespaces and the array is printed as a string of digits s and all we
# know is that all integers in the array were in the range [1, k] and there are
# no leading zeros in the array.
#
# Given the string s and the integer k, return the number of the possible
# arrays that can be printed as s using the mentioned program. Since the answer
# may be very large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: s = "1000", k = 10000
# Output: 1
# Explanation: The only possible array is [1000]
#
# Example 2:
#
# Input: s = "1000", k = 10
# Output: 0
# Explanation: There cannot be an array that was printed this way and has all
# integer >= 1 and <= 10.
#
# Example 3:
#
# Input: s = "1317", k = 2000
# Output: 8
# Explanation: Possible arrays are
# [1317],[131,7],[13,17],[1,317],[13,1,7],[1,31,7],[1,3,17],[1,3,1,7]
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists of only digits and does not contain leading zeros.
#
# 1 <= k <= 10^9
#

# @lc code=start
from functools import lru_cache


class Solution:
    def numberOfArrays(self, s: str, k: int) -> int:
        """
        Interview explanation:
        Count ways to split digit string into integers in [1,k] (no leading zeros).
        DP: dp[i] = ways for suffix s[i:]; try lengths while number <=k.

        Algorithm:
        (bottom-up DP)
        - dp[n]=1; for i from n-1..0: if s[i]!='0', accumulate valid prefixes.

        Complexity: O(n * log10 k) time, O(n) space.
        """
        MOD = 10**9 + 7
        n = len(s)
        dp = [0] * (n + 1)
        dp[n] = 1
        for i in range(n - 1, -1, -1):
            if s[i] == "0":
                continue
            num = 0
            for j in range(i, n):
                num = num * 10 + ord(s[j]) - 48
                if num > k:
                    break
                dp[i] = (dp[i] + dp[j + 1]) % MOD
        return dp[0]

    def numberOfArrays_memo(self, s: str, k: int) -> int:
        """
        Interview explanation:
        Alternate top-down memo of the same digit-DP transitions.

        Algorithm:
        - dfs(i): ways from i; try ending j with int(s[i:j+1]) in range.

        Complexity: O(n log k) time, O(n) space.
        """
        MOD = 10**9 + 7
        n = len(s)

        @lru_cache(None)
        def dfs(i: int) -> int:
            if i == n:
                return 1
            if s[i] == "0":
                return 0
            ans = 0
            num = 0
            for j in range(i, n):
                num = num * 10 + ord(s[j]) - 48
                if num > k:
                    break
                ans = (ans + dfs(j + 1)) % MOD
            return ans

        return dfs(0)
# @lc code=end
