#
# @lc app=leetcode id=1449 lang=python3
#
# [1449] Form Largest Integer With Digits That Add up to Target
#
# https://leetcode.com/problems/form-largest-integer-with-digits-that-add-up-to-target/description/
#
# algorithms
# Hard (49.9%)
# Likes:    727
# Dislikes: 20
# Total Accepted:    24.2K
# Total Submissions: 48.6K
# Testcase Example:  "[4,3,2,5,6,7,2,5,5]"
#
# Given an array of integers cost and an integer target, return the maximum
# integer you can paint under the following rules:
#
# The cost of painting a digit (i + 1) is given by cost[i] (0-indexed).
#
# The total cost used must be equal to target.
#
# The integer does not have 0 digits.
#
# Since the answer may be very large, return it as a string. If there is no way
# to paint any integer given the condition, return "0".
#
# Example 1:
#
# Input: cost = [4,3,2,5,6,7,2,5,5], target = 9
# Output: "7772"
# Explanation: The cost to paint the digit '7' is 2, and the digit '2' is 3.
# Then cost("7772") = 2*3+ 3*1 = 9. You could also paint "977", but "7772" is
# the largest number.
# Digit cost
# 1 -> 4
# 2 -> 3
# 3 -> 2
# 4 -> 5
# 5 -> 6
# 6 -> 7
# 7 -> 2
# 8 -> 5
# 9 -> 5
#
# Example 2:
#
# Input: cost = [7,6,5,5,5,6,8,7,8], target = 12
# Output: "85"
# Explanation: The cost to paint the digit '8' is 7, and the digit '5' is 5.
# Then cost("85") = 7 + 5 = 12.
#
# Example 3:
#
# Input: cost = [2,4,6,2,4,6,4,4,4], target = 5
# Output: "0"
# Explanation: It is impossible to paint any integer with total cost equal to
# target.
#
# Constraints:
#
# cost.length == 9
#
# 1 <= cost[i], target <= 5000
#

# @lc code=start
from typing import List
from functools import lru_cache


class Solution:
    def largestNumber(self, cost: List[int], target: int) -> str:
        """
        Interview explanation:
        Digits 1..9 cost cost[d-1]; paint target exactly; form largest number
        (length then lex). Unbounded knapsack on cost: dp[t] = best digit string
        for sum t; compare by length then lexicographic.

        Algorithm:
        (DP)
        - dp[0]=""; others None; for t, for digit 9..1: if prev: candidate=digit+dp[t-c]; take better.

        Complexity: O(target * 9 * L) time, O(target * L) space.
        """
        dp = [None] * (target + 1)
        dp[0] = ""

        def better(a: str, b: str) -> str:
            if a is None:
                return b
            if b is None:
                return a
            if len(a) != len(b):
                return a if len(a) > len(b) else b
            return a if a > b else b

        for t in range(1, target + 1):
            best = None
            for d in range(9, 0, -1):
                c = cost[d - 1]
                if t >= c and dp[t - c] is not None:
                    cand = str(d) + dp[t - c]
                    best = better(best, cand)
            dp[t] = best
        return dp[target] if dp[target] is not None else "0"

    def largestNumber_memo(self, cost: List[int], target: int) -> str:
        """
        Interview explanation:
        Alternate top-down: dfs(remain) returns best string for exact remain.

        Algorithm:
        - Memo; try digits 9..1; pick better concatenation.

        Complexity: O(target * 9 * L) time, O(target * L) space.
        """
        def better(a, b):
            if a is None:
                return b
            if b is None:
                return a
            if len(a) != len(b):
                return a if len(a) > len(b) else b
            return max(a, b)

        @lru_cache(None)
        def dfs(remain: int):
            if remain == 0:
                return ""
            if remain < 0:
                return None
            best = None
            for d in range(9, 0, -1):
                nxt = dfs(remain - cost[d - 1])
                if nxt is not None:
                    best = better(best, str(d) + nxt)
            return best

        ans = dfs(target)
        return ans if ans is not None else "0"
# @lc code=end
