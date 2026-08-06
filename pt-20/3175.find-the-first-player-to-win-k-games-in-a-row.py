#
# @lc app=leetcode id=3175 lang=python3
#
# [3175] Find The First Player to win K Games in a Row
#
# https://leetcode.com/problems/find-the-first-player-to-win-k-games-in-a-row/description/
#
# algorithms
# Medium (40.46%)
# Likes:    143
# Dislikes: 16
# Total Accepted:    37.4K
# Total Submissions: 92.5K
# Testcase Example:  "[4,2,6,3,9]\n2"
#
#
# A competition consists of n players numbered from 0 to n - 1.
#
# You are given an integer array skills of size n and a positive integer
# k, where skills[i] is the skill level of player i. All integers in
# skills are unique.
#
# All players are standing in a queue in order from player 0 to player n -
# 1.
#
# The competition process is as follows:
#
# The first two players in the queue play a game, and the player with the
# higher skill level wins.
#
# After the game, the winner stays at the beginning of the queue, and the
# loser goes to the end of it.
#
# The winner of the competition is the first player who wins k games in a
# row.
#
# Return the initial index of the winning player.
#
# Example 1:
#
# Input: skills = [4,2,6,3,9], k = 2
#
# Output: 2
#
# Explanation:
#
# Initially, the queue of players is [0,1,2,3,4]. The following process
# happens:
#
# Players 0 and 1 play a game, since the skill of player 0 is higher than
# that of player 1, player 0 wins. The resulting queue is [0,2,3,4,1].
#
# Players 0 and 2 play a game, since the skill of player 2 is higher than
# that of player 0, player 2 wins. The resulting queue is [2,3,4,1,0].
#
# Players 2 and 3 play a game, since the skill of player 2 is higher than
# that of player 3, player 2 wins. The resulting queue is [2,4,1,0,3].
#
# Player 2 won k = 2 games in a row, so the winner is player 2.
#
# Example 2:
#
# Input: skills = [2,5,4], k = 3
#
# Output: 1
#
# Explanation:
#
# Initially, the queue of players is [0,1,2]. The following process
# happens:
#
# Players 0 and 1 play a game, since the skill of player 1 is higher than
# that of player 0, player 1 wins. The resulting queue is [1,2,0].
#
# Players 1 and 2 play a game, since the skill of player 1 is higher than
# that of player 2, player 1 wins. The resulting queue is [1,0,2].
#
# Players 1 and 0 play a game, since the skill of player 1 is higher than
# that of player 0, player 1 wins. The resulting queue is [1,2,0].
#
# Player 1 won k = 3 games in a row, so the winner is player 1.
#
# Constraints:
#
# n == skills.length
#
# 2 <= n <= 10^5
#
# 1 <= k <= 10^9
#
# 1 <= skills[i] <= 10^6
#
# All integers in skills are unique.
#

# @lc code=start
from typing import List


class Solution:
    def findWinningPlayer(self, skills: List[int], k: int) -> int:
        """
        Interview explanation:
        The queue simulation is a "current champion vs next challenger" process.
        Once someone beats k in a row, they win; if k is huge, the global max wins.

        Algorithm:
        - Track champion index and win streak; scan challengers left to right.
        - If k >= n-1, return index of maximum skill (must eventually win).

        Complexity: O(n) time, O(1) space.
        """
        n = len(skills)
        if k >= n - 1:
            return max(range(n), key=lambda i: skills[i])
        cur = 0
        streak = 0
        for i in range(1, n):
            if skills[cur] > skills[i]:
                streak += 1
            else:
                cur = i
                streak = 1
            if streak == k:
                return cur
        return cur

    def findWinningPlayer_deque(self, skills: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: simulate with a deque of indices (safe because a full pass
        without k-streak implies the max is champion).

        Algorithm:
        - Pop front two, push winner front / loser back; count consecutive wins.

        Complexity: O(n) time, O(n) space.
        """
        from collections import deque

        n = len(skills)
        if k >= n - 1:
            return max(range(n), key=lambda i: skills[i])
        q = deque(range(n))
        wins = 0
        while wins < k:
            a = q.popleft()
            b = q.popleft()
            if skills[a] > skills[b]:
                wins += 1
                q.appendleft(a)
                q.append(b)
            else:
                wins = 1
                q.appendleft(b)
                q.append(a)
        return q[0]
# @lc code=end
