#
# @lc app=leetcode id=1414 lang=python3
#
# [1414] Find the Minimum Number of Fibonacci Numbers Whose Sum Is K
#
# https://leetcode.com/problems/find-the-minimum-number-of-fibonacci-numbers-whose-sum-is-k/description/
#
# algorithms
# Medium (64.71%)
# Likes:    1056
# Dislikes: 68
# Total Accepted:    53.9K
# Total Submissions: 83.3K
# Testcase Example:  "7"
#
# Given an integer k, return the minimum number of Fibonacci numbers whose sum
# is equal to k. The same Fibonacci number can be used multiple times.
#
# The Fibonacci numbers are defined as:
#
# F_1 = 1
#
# F_2 = 1
#
# F_n = F_n-1 + F_n-2 for n > 2.
#
# It is guaranteed that for the given constraints we can always find such
# Fibonacci numbers that sum up to k.
#
# Example 1:
#
# Input: k = 7
# Output: 2
# Explanation: The Fibonacci numbers are: 1, 1, 2, 3, 5, 8, 13, ...
# For k = 7 we can use 2 + 5 = 7.
#
# Example 2:
#
# Input: k = 10
# Output: 2
# Explanation: For k = 10 we can use 2 + 8 = 10.
#
# Example 3:
#
# Input: k = 19
# Output: 3
# Explanation: For k = 19 we can use 1 + 5 + 13 = 19.
#
# Constraints:
#
# 1 <= k <= 10^9
#

# @lc code=start
class Solution:
    def findMinFibonacciNumbers(self, k: int) -> int:
        """
        Interview explanation:
        Zeckendorf: every positive integer is uniquely sum of non-consecutive
        Fibonaccis; greedy take largest Fib <= remaining is optimal for count
        (with repeats allowed here, greedy still optimal).

        Algorithm:
        (greedy)
        - Generate Fibs <= k; while k: subtract largest <=k; count++.

        Complexity: O(log k) Fibs, O(log^2 k) time, O(log k) space.
        """
        fibs = [1, 1]
        while fibs[-1] <= k:
            fibs.append(fibs[-1] + fibs[-2])
        fibs.pop()
        ans = 0
        i = len(fibs) - 1
        while k:
            if fibs[i] <= k:
                k -= fibs[i]
                ans += 1
            else:
                i -= 1
        return ans

    def findMinFibonacciNumbers_dp(self, k: int) -> int:
        """
        Interview explanation:
        Alternate unbounded knapsack DP with Fibonacci denominations (small for demo;
        for large k prefer greedy). Here k fits interview constraints typically.

        Algorithm:
        - Fib list; dp[x]=min coins; classic coin change.

        Complexity: O(k * #fibs) time, O(k) space.
        """
        if k <= 1:
            return k
        fibs = [1, 1]
        while fibs[-1] <= k:
            fibs.append(fibs[-1] + fibs[-2])
        fibs.pop()
        # unique fibs
        fibs = sorted(set(fibs))
        INF = 10**9
        dp = [INF] * (k + 1)
        dp[0] = 0
        for x in range(1, k + 1):
            for f in fibs:
                if f > x:
                    break
                dp[x] = min(dp[x], dp[x - f] + 1)
        return dp[k]
# @lc code=end
