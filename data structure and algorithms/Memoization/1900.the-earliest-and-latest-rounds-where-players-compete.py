#
# @lc app=leetcode id=1900 lang=python3
#
# [1900] The Earliest and Latest Rounds Where Players Compete
#
# https://leetcode.com/problems/the-earliest-and-latest-rounds-where-players-compete/description/
#
# algorithms
# Hard (72.07%)
# Likes:    522
# Dislikes: 80
# Total Accepted:    62.7K
# Total Submissions: 87.0K
# Testcase Example:  "11"
#
# There is a tournament where n players are participating. The players are
# standing in a single row and are numbered from 1 to n based on their initial
# standing position (player 1 is the first player in the row, player 2 is the
# second player in the row, etc.).
#
# The tournament consists of multiple rounds (starting from round number 1). In
# each round, the i^th player from the front of the row competes against the
# i^th player from the end of the row, and the winner advances to the next
# round. When the number of players is odd for the current round, the player in
# the middle automatically advances to the next round.
#
# For example, if the row consists of players 1, 2, 4, 6, 7
#
# Player 1 competes against player 7.
#
# Player 2 competes against player 6.
#
# Player 4 automatically advances to the next round.
#
# After each round is over, the winners are lined back up in the row based on
# the original ordering assigned to them initially (ascending order).
#
# The players numbered firstPlayer and secondPlayer are the best in the
# tournament. They can win against any other player before they compete against
# each other. If any two other players compete against each other, either of
# them might win, and thus you may choose the outcome of this round.
#
# Given the integers n, firstPlayer, and secondPlayer, return an integer array
# containing two values, the earliest possible round number and the latest
# possible round number in which these two players will compete against each
# other, respectively.
#
# Example 1:
#
# Input: n = 11, firstPlayer = 2, secondPlayer = 4
# Output: [3,4]
# Explanation:
# One possible scenario which leads to the earliest round number:
# First round: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11
# Second round: 2, 3, 4, 5, 6, 11
# Third round: 2, 3, 4
# One possible scenario which leads to the latest round number:
# First round: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11
# Second round: 1, 2, 3, 4, 5, 6
# Third round: 1, 2, 4
# Fourth round: 2, 4
#
# Example 2:
#
# Input: n = 5, firstPlayer = 1, secondPlayer = 5
# Output: [1,1]
# Explanation: The players numbered 1 and 5 compete in the first round.
# There is no way to make them compete in any other round.
#
# Constraints:
#
# 2 <= n <= 28
#
# 1 <= firstPlayer < secondPlayer <= n
#

# @lc code=start
from typing import List
from functools import lru_cache
import math


class Solution:
    def earliestAndLatest(self, n: int, firstPlayer: int, secondPlayer: int) -> List[int]:
        """
        Interview explanation:
        Bracket tournament: position i plays n+1-i; other matches can go either
        way. Find earliest/latest round when two players meet. Represent them as
        (l = distance from front, r = distance from end) among k players.

        Algorithm (memo DP on (l,r,k)):
        - If l==r they meet this round → (1,1).
        - Enumerate next-round ranks i,j of the two players among (k+1)//2
          survivors with valid range l+r-k//2 ≤ i+j ≤ (k+1)//2.
        - Recurse; answer is min/max of 1+sub.

        Complexity: O(n^4) states/transitions roughly, fine for n≤28.
        """
        @lru_cache(None)
        def dp(l: int, r: int, k: int) -> tuple:
            # first is l-th from front; second is r-th from end among k players
            if l == r:
                return (1, 1)
            if l > r:
                return dp(r, l, k)
            a, b = math.inf, -math.inf
            for i in range(1, l + 1):
                for j in range(l - i + 1, r - i + 1):
                    if not (l + r - k // 2 <= i + j <= (k + 1) // 2):
                        continue
                    x, y = dp(i, j, (k + 1) // 2)
                    a = min(a, x + 1)
                    b = max(b, y + 1)
            return (a, b)

        return list(dp(firstPlayer, n - secondPlayer + 1, n))

    def earliestAndLatest_enumerate(self, n: int, firstPlayer: int, secondPlayer: int) -> List[int]:
        """
        Interview explanation:
        Alternate: explicitly enumerate winners of non-special matches via bit
        masks; recurse on survivor list. Clearer but heavier for interviews.

        Algorithm:
        - Pair ends; force both specials to advance; for other pairs try both
          winners; recurse with remapped positions.

        Complexity: exponential with memo on (n,i,j); OK for n≤28 with pruning.
        """
        @lru_cache(None)
        def dfs(nn: int, i: int, j: int):
            if i > j:
                i, j = j, i
            if i + j == nn + 1:
                return (1, 1)
            pairs = []
            for k in range(1, nn // 2 + 1):
                left, right = k, nn - k + 1
                if left not in (i, j) and right not in (i, j):
                    pairs.append((left, right))
            mid = (nn + 1) // 2 if nn % 2 else None
            m = (nn + 1) // 2
            early, late = math.inf, 0
            tot = len(pairs)
            for mask in range(1 << tot):
                surv = [i, j]
                for idx, (left, right) in enumerate(pairs):
                    surv.append(right if (mask >> idx) & 1 else left)
                if mid is not None and mid not in (i, j):
                    surv.append(mid)
                surv.sort()
                e1, l1 = dfs(m, surv.index(i) + 1, surv.index(j) + 1)
                early = min(early, e1 + 1)
                late = max(late, l1 + 1)
            return (early, late)

        return list(dfs(n, firstPlayer, secondPlayer))
# @lc code=end
