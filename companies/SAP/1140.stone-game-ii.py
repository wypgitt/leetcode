#
# @lc app=leetcode id=1140 lang=python3
#
# [1140] Stone Game II
#
# https://leetcode.com/problems/stone-game-ii/description/
#
# algorithms
# Medium (72.72%)
# Likes:    3524
# Dislikes: 942
# Total Accepted:    205K
# Total Submissions: 282K
# Testcase Example:  "[2,7,9,4,4]"
#
# Alice and Bob continue their games with piles of stones. There are a number
# of piles arranged in a row, and each pile has a positive integer number of
# stones piles[i]. The objective of the game is to end with the most stones.
#
# Alice and Bob take turns, with Alice starting first.
#
# On each player's turn, that player can take all the stones in the first X
# remaining piles, where 1 <= X <= 2M. Then, we set M = max(M, X). Initially, M
# = 1.
#
# The game continues until all the stones have been taken.
#
# Assuming Alice and Bob play optimally, return the maximum number of stones
# Alice can get.
#
# Example 1:
#
# Input: piles = [2,7,9,4,4]
#
# Output: 10
#
# Explanation:
#
# If Alice takes one pile at the beginning, Bob takes two piles, then Alice
# takes 2 piles again. Alice can get 2 + 4 + 4 = 10 stones in total.
#
# If Alice takes two piles at the beginning, then Bob can take all three piles
# left. In this case, Alice get 2 + 7 = 9 stones in total.
#
# So we return 10 since it's larger.
#
# Example 2:
#
# Input: piles = [1,2,3,4,5,100]
#
# Output: 104
#
# Constraints:
#
# 1 <= piles.length <= 100
#
# 1 <= piles[i] <= 10^4
#

# @lc code=start
from typing import List
from functools import lru_cache


class Solution:
    def stoneGameII(self, piles: List[int]) -> int:
        """
        Interview explanation:
        Alice/Bob optimally take X in [1,2M] piles from the front, then M:=max(M,X).
        DP: maximize stones for the current player; Alice starts with M=1.
        Return Alice's stones (total - Bob = 2*Alice - total, or directly Alice).

        Algorithm (DP):
        - suffix[i] = sum(piles[i:]).
        - dfs(i, M) = max stones current player can get from piles[i:] with M.
        - dfs(i,M) = max over X: suffix[i] - dfs(i+X, max(M,X)).

        Complexity: O(n^2) states * O(n) transitions ≈ O(n^3), O(n^2) space.
        """
        n = len(piles)
        suffix = [0] * (n + 1)
        for i in range(n - 1, -1, -1):
            suffix[i] = suffix[i + 1] + piles[i]

        @lru_cache(None)
        def dfs(i: int, M: int) -> int:
            if i >= n:
                return 0
            if i + 2 * M >= n:
                return suffix[i]
            best = 0
            for X in range(1, 2 * M + 1):
                best = max(best, suffix[i] - dfs(i + X, max(M, X)))
            return best

        return dfs(0, 1)
# @lc code=end
