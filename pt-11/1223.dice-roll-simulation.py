#
# @lc app=leetcode id=1223 lang=python3
#
# [1223] Dice Roll Simulation
#
# https://leetcode.com/problems/dice-roll-simulation/description/
#
# algorithms
# Hard (51.16%)
# Likes:    1008
# Dislikes: 199
# Total Accepted:    39.2K
# Total Submissions: 76.6K
# Testcase Example:  "2"
#
# A die simulator generates a random number from 1 to 6 for each roll. You
# introduced a constraint to the generator such that it cannot roll the number
# i more than rollMax[i] (1-indexed) consecutive times.
#
# Given an array of integers rollMax and an integer n, return the number of
# distinct sequences that can be obtained with exact n rolls. Since the answer
# may be too large, return it modulo 10^9 + 7.
#
# Two sequences are considered different if at least one element differs from
# each other.
#
# Example 1:
#
# Input: n = 2, rollMax = [1,1,2,2,2,3]
# Output: 34
# Explanation: There will be 2 rolls of die, if there are no constraints on the
# die, there are 6 * 6 = 36 possible combinations. In this case, looking at
# rollMax array, the numbers 1 and 2 appear at most once consecutively,
# therefore sequences (1,1) and (2,2) cannot occur, so the final answer is 36-2
# = 34.
#
# Example 2:
#
# Input: n = 2, rollMax = [1,1,1,1,1,1]
# Output: 30
#
# Example 3:
#
# Input: n = 3, rollMax = [1,1,1,2,2,3]
# Output: 181
#
# Constraints:
#
# 1 <= n <= 5000
#
# rollMax.length == 6
#
# 1 <= rollMax[i] <= 15
#


# @lc code=start
from typing import List

class Solution:
    def dieSimulator(self, n: int, rollMax: List[int]) -> int:
        """
        Interview explanation:
        Number of distinct die sequences of length n where face i+1 cannot
        appear more than rollMax[i] times consecutively. DP[len][face][streak].

        Algorithm:
        - dp[i][j] = ways length i ending with face j (any streak) via 3D or
          roll-by-roll: for each prev face/streak, append same (if streak<max)
          or different face (streak=1)

        Complexity: O(n * 6 * max(rollMax)) ~ O(n*6*15).
        """
        MOD = 10**9 + 7
        # dp[face][streak-1] after processing current length
        dp = [[0] * 15 for _ in range(6)]
        for f in range(6):
            dp[f][0] = 1
        for _ in range(n - 1):
            ndp = [[0] * 15 for _ in range(6)]
            for f in range(6):
                for s in range(rollMax[f]):
                    if dp[f][s] == 0:
                        continue
                    # same face
                    if s + 1 < rollMax[f]:
                        ndp[f][s + 1] = (ndp[f][s + 1] + dp[f][s]) % MOD
                    # different faces
                    for nf in range(6):
                        if nf != f:
                            ndp[nf][0] = (ndp[nf][0] + dp[f][s]) % MOD
            dp = ndp
        return sum(sum(row) for row in dp) % MOD
# @lc code=end
