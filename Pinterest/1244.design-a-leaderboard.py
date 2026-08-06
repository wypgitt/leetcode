#
# @lc app=leetcode id=1244 lang=python3
#
# [1244] Design A Leaderboard
#
# https://leetcode.com/problems/design-a-leaderboard/description/
#
# algorithms
# Medium (68.05%)
# Likes:    825
# Dislikes: 99
# Total Accepted:    101.8K
# Total Submissions: 149.6K
# Testcase Example:  "[\"Leaderboard\",\"addScore\",\"addScore\",\"addScore\",\"addScore\",\"addScore\",\"top\",\"reset\",\"reset\",\"addScore\",\"top\"]\n[[],[1,73],[2,56],[3,39],[4,51],[5,4],[1],[1],[2],[2,51],[3]]"
#
#
# Design a Leaderboard class, which has 3 functions:
#
# addScore(playerId, score): Update the leaderboard by adding score to the
# given player's score. If there is no player with such id in the
# leaderboard, add him to the leaderboard with the given score.
#
# top(K): Return the score sum of the top K players.
#
# reset(playerId): Reset the score of the player with the given id to 0
# (in other words erase it from the leaderboard). It is guaranteed that
# the player was added to the leaderboard before calling this function.
#
# Initially, the leaderboard is empty.
#
# Example 1:
#
# Input:
# ["Leaderboard","addScore","addScore","addScore","addScore","addScore","top","reset","reset","addScore","top"]
# [[],[1,73],[2,56],[3,39],[4,51],[5,4],[1],[1],[2],[2,51],[3]]
# Output:
# [null,null,null,null,null,null,73,null,null,null,141]
#
# Explanation:
# Leaderboard leaderboard = new Leaderboard ();
# leaderboard.addScore(1,73);   // leaderboard = [[1,73]];
# leaderboard.addScore(2,56);   // leaderboard = [[1,73],[2,56]];
# leaderboard.addScore(3,39);   // leaderboard = [[1,73],[2,56],[3,39]];
# leaderboard.addScore(4,51);   // leaderboard =
# [[1,73],[2,56],[3,39],[4,51]];
# leaderboard.addScore(5,4);    // leaderboard =
# [[1,73],[2,56],[3,39],[4,51],[5,4]];
# leaderboard.top(1);           // returns 73;
# leaderboard.reset(1);         // leaderboard =
# [[2,56],[3,39],[4,51],[5,4]];
# leaderboard.reset(2);         // leaderboard = [[3,39],[4,51],[5,4]];
# leaderboard.addScore(2,51);   // leaderboard =
# [[2,51],[3,39],[4,51],[5,4]];
# leaderboard.top(3);           // returns 141 = 51 + 51 + 39;
#
# Constraints:
#
# 1 <= playerId, K <= 10000
#
# It's guaranteed that K is less than or equal to the current number of
# players.
#
# 1 <= score <= 100
#
# There will be at most 1000 function calls.
#
# @lc code=start
import heapq
from typing import Dict

class Leaderboard:
    def __init__(self):
        """
        Interview explanation:
        Premium design. Maintain playerId → score. addScore accumulates; top(K)
        sums K largest scores; reset removes player. Hash map + sort/heap for top.

        Algorithm:
        - self.scores: Dict[int,int] empty

        Complexity: O(1) init.
        """
        self.scores: Dict[int, int] = {}

    def addScore(self, playerId: int, score: int) -> None:
        """
        Interview explanation:
        Add `score` to playerId (create entry if new).

        Algorithm:
        - scores[playerId] = scores.get(playerId, 0) + score

        Complexity: O(1).
        """
        self.scores[playerId] = self.scores.get(playerId, 0) + score

    def top(self, K: int) -> int:
        """
        Interview explanation:
        Return sum of the top K scores. Use heapq.nlargest or sort descending.

        Algorithm:
        - sum(heapq.nlargest(K, scores.values()))

        Complexity: O(n log K) with nlargest.
        """
        return sum(heapq.nlargest(K, self.scores.values()))

    def top_sort(self, K: int) -> int:
        """
        Interview explanation:
        Alternate: fully sort score values descending and sum first K.

        Algorithm:
        - sum(sorted(values, reverse=True)[:K])

        Complexity: O(n log n).
        """
        return sum(sorted(self.scores.values(), reverse=True)[:K])

    def reset(self, playerId: int) -> None:
        """
        Interview explanation:
        Reset player score to 0 by deleting the player from the map.

        Algorithm:
        - del scores[playerId] if present

        Complexity: O(1).
        """
        if playerId in self.scores:
            del self.scores[playerId]
# @lc code=end
