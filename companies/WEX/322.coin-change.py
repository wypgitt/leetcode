#
# @lc app=leetcode id=322 lang=python3
#
# [322] Coin Change
#
# https://leetcode.com/problems/coin-change/description/
#
# algorithms
# Medium (48.9%)
# Likes:    21193
# Dislikes: 549
# Total Accepted:    3.0M
# Total Submissions: 6.1M
# Testcase Example:  "[1,2,5]"
#
# You are given an integer array coins representing coins of different
# denominations and an integer amount representing a total amount of money.
#
# Return the fewest number of coins that you need to make up that amount. If
# that amount of money cannot be made up by any combination of the coins,
# return -1.
#
# You may assume that you have an infinite number of each kind of coin.
#
# Example 1:
#
# Input: coins = [1,2,5], amount = 11
# Output: 3
# Explanation: 11 = 5 + 5 + 1
#
# Example 2:
#
# Input: coins = [2], amount = 3
# Output: -1
#
# Example 3:
#
# Input: coins = [1], amount = 0
# Output: 0
#
# Constraints:
#
# 1 <= coins.length <= 12
#
# 1 <= coins[i] <= 2^31 - 1
#
# 0 <= amount <= 10^4
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def coinChange(self, coins: List[int], amount: int) -> int:
        """
        Interview explanation:
        Unbounded knapsack DP: dp[x] = fewest coins to make amount x.
        Transition: for each coin c, dp[x] = min(dp[x], dp[x-c] + 1).

        Algorithm:
        - dp[0] = 0; others = inf.
        - For each amount x, try every coin that fits.
        - Return dp[amount] or -1 if unreachable.

        Complexity: O(amount * len(coins)) time, O(amount) space.
        """
        dp = [0] + [amount + 1] * amount
        for x in range(1, amount + 1):
            for c in coins:
                if c <= x:
                    dp[x] = min(dp[x], dp[x - c] + 1)
        return dp[amount] if dp[amount] <= amount else -1

    def coinChange_bfs(self, coins: List[int], amount: int) -> int:
        """
        Interview explanation:
        Alternate best: BFS by coin count. Each level adds one more coin;
        first time we hit amount is the minimum number of coins.

        Algorithm:
        - Queue of remaining amounts; visited set.
        - From rem, enqueue rem - c for each coin if rem - c >= 0.
        - Return steps when rem == 0.

        Complexity: O(amount * len(coins)) time/space worst case.
        """
        if amount == 0:
            return 0
        q = deque([amount])
        visited = {amount}
        steps = 0
        while q:
            steps += 1
            for _ in range(len(q)):
                rem = q.popleft()
                for c in coins:
                    nxt = rem - c
                    if nxt == 0:
                        return steps
                    if nxt > 0 and nxt not in visited:
                        visited.add(nxt)
                        q.append(nxt)
        return -1
# @lc code=end
