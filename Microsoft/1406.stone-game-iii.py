#
# @lc app=leetcode id=1406 lang=python3
#
# [1406] Stone Game III
#
# https://leetcode.com/problems/stone-game-iii/description/
#
# algorithms
# Hard (68.01%)
# Likes:    2567
# Dislikes: 88
# Total Accepted:    206K
# Total Submissions: 303K
# Testcase Example:  "[1,2,3,7]"
#
# Alice and Bob continue their games with piles of stones. There are several
# stones arranged in a row, and each stone has an associated value which is an
# integer given in the array stoneValue.
#
# Alice and Bob take turns, with Alice starting first. On each player's turn,
# that player can take 1, 2, or 3 stones from the first remaining stones in the
# row.
#
# The score of each player is the sum of the values of the stones taken. The
# score of each player is 0 initially.
#
# The objective of the game is to end with the highest score, and the winner is
# the player with the highest score and there could be a tie. The game
# continues until all the stones have been taken.
#
# Assume Alice and Bob play optimally.
#
# Return "Alice" if Alice will win, "Bob" if Bob will win, or "Tie" if they
# will end the game with the same score.
#
# Example 1:
#
# Input: stoneValue = [1,2,3,7]
# Output: "Bob"
# Explanation: Alice will always lose. Her best move will be to take three
# piles and the score become 6. Now the score of Bob is 7 and Bob wins.
#
# Example 2:
#
# Input: stoneValue = [1,2,3,-9]
# Output: "Alice"
# Explanation: Alice must choose all the three piles at the first move to win
# and leave Bob with negative score.
# If Alice chooses one pile her score will be 1 and the next move Bob's score
# becomes 5. In the next move, Alice will take the pile with value = -9 and
# lose.
# If Alice chooses two piles her score will be 3 and the next move Bob's score
# becomes 3. In the next move, Alice will take the pile with value = -9 and
# also lose.
# Remember that both play optimally so here Alice will choose the scenario that
# makes her win.
#
# Example 3:
#
# Input: stoneValue = [1,2,3,6]
# Output: "Tie"
# Explanation: Alice cannot win this game. She can end the game in a draw if
# she decided to choose all the first three piles, otherwise she will lose.
#
# Constraints:
#
# 1 <= stoneValue.length <= 5 * 10^4
#
# -1000 <= stoneValue[i] <= 1000
#

# @lc code=start
from typing import List
from functools import lru_cache


class Solution:
    def stoneGameIII(self, stoneValue: List[int]) -> str:
        """
        Interview explanation:
        Alice and Bob optimally take 1..3 stones from the front of the remaining
        suffix. Score difference (Alice-Bob) from a position: take sum of next
        i stones minus opponent's best from i ahead. Bottom-up DP from the end.

        Algorithm:
        (DP)
        - dp[i] = max score diff starting at i; dp[n]=0
        - dp[i] = max(sum(stone[i:i+k]) - dp[i+k] for k=1..3 if i+k<=n)
        - Compare dp[0] to 0 → Alice/Bob/Tie

        Complexity: O(n) time, O(n) space (can optimize to O(1)).
        """
        n = len(stoneValue)
        dp = [0] * (n + 1)
        for i in range(n - 1, -1, -1):
            best = float("-inf")
            take = 0
            for k in range(1, 4):
                if i + k - 1 >= n:
                    break
                take += stoneValue[i + k - 1]
                best = max(best, take - dp[i + k])
            dp[i] = best
        if dp[0] > 0:
            return "Alice"
        if dp[0] < 0:
            return "Bob"
        return "Tie"

    def stoneGameIII_memo(self, stoneValue: List[int]) -> str:
        """
        Interview explanation:
        Alternate top-down memoization of the same optimal game-theory recurrence.

        Algorithm:
        - @cache dfs(i): max diff from index i; same take 1..3 transition.

        Complexity: O(n) time, O(n) space.
        """
        n = len(stoneValue)

        @lru_cache(None)
        def dfs(i: int) -> int:
            if i >= n:
                return 0
            best, take = float("-inf"), 0
            for k in range(1, 4):
                if i + k - 1 >= n:
                    break
                take += stoneValue[i + k - 1]
                best = max(best, take - dfs(i + k))
            return best

        diff = dfs(0)
        if diff > 0:
            return "Alice"
        if diff < 0:
            return "Bob"
        return "Tie"
# @lc code=end
