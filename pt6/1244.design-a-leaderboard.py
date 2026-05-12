#
# @lc app=leetcode id=1244 lang=python3
#
# [1244] Design A Leaderboard
#
# https://leetcode.com/problems/design-a-leaderboard/description/
#
# algorithms
# Medium (68.08%)
# Likes:    822
# Dislikes: 98
# Total Accepted:    99.2K
# Total Submissions: 145.7K
# Testcase Example:  '["Leaderboard","addScore","addScore","addScore","addScore","addScore","top","reset","reset","addScore","top"]\n' +
# '[[],[1,73],[2,56],[3,39],[4,51],[5,4],[1],[1],[2],[2,51],[3]]'
#
# Design a Leaderboard class, which has 3 functions:
# 
# 
# addScore(playerId, score): Update the leaderboard by adding score to the
# given player's score. If there is no player with such id in the leaderboard,
# add him to the leaderboard with the given score.
# top(K): Return the score sum of the top K players.
# reset(playerId): Reset the score of the player with the given id to 0 (in
# other words erase it from the leaderboard). It is guaranteed that the player
# was added to the leaderboard before calling this function.
# 
# 
# Initially, the leaderboard is empty.
# 
# 
# Example 1:
# 
# 
# Input: 
# 
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
# leaderboard.addScore(4,51);   // leaderboard = [[1,73],[2,56],[3,39],[4,51]];
# leaderboard.addScore(5,4);    // leaderboard =
# [[1,73],[2,56],[3,39],[4,51],[5,4]];
# leaderboard.top(1);           // returns 73;
# leaderboard.reset(1);         // leaderboard = [[2,56],[3,39],[4,51],[5,4]];
# leaderboard.reset(2);         // leaderboard = [[3,39],[4,51],[5,4]];
# leaderboard.addScore(2,51);   // leaderboard = [[2,51],[3,39],[4,51],[5,4]];
# leaderboard.top(3);           // returns 141 = 51 + 51 + 39;
# 
# 
# 
# Constraints:
# 
# 
# 1 <= playerId, K <= 10000
# It's guaranteed that K is less than or equal to the current number of
# players.
# 1 <= score <= 100
# There will be at most 1000 function calls.
# 
# 
#

# @lc code=start
class Leaderboard:

    def __init__(self):
        self.scores = {}

    def addScore(self, playerId: int, score: int) -> None:
        self.scores[playerId] = self.scores.get(playerId, 0) + score

    def top(self, K: int) -> int:
        return sum(sorted(self.scores.values(), reverse=True)[:K])

    def reset(self, playerId: int) -> None:
        del self.scores[playerId]


# Your Leaderboard object will be instantiated and called as such:
# obj = Leaderboard()
# obj.addScore(playerId,score)
# param_2 = obj.top(K)
# obj.reset(playerId)
# @lc code=end

# Explanation
# -----------
# Store player scores in a dictionary keyed by playerId. addScore is a direct
# update, reset deletes the player, and top(K) sorts current scores descending
# and sums the first K.
#
# The constraints allow at most 1000 calls, so this simple dictionary plus sort
# is clearer than maintaining a balanced tree or heap with lazy deletion. In an
# interview, mention that a production leaderboard with many top queries could
# use a sorted container or Fenwick tree over bounded scores.
#
# Edge cases: addScore on a new player starts from zero; reset is guaranteed to
# target an existing player; K is guaranteed not to exceed the player count.
#
# Time complexity: addScore O(1), reset O(1), top O(n log n).
# Space complexity: O(n), one score per active player.
