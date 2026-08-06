#
# @lc app=leetcode id=1823 lang=python3
#
# [1823] Find the Winner of the Circular Game
#
# https://leetcode.com/problems/find-the-winner-of-the-circular-game/description/
#
# algorithms
# Medium (82.32%)
# Likes:    4138
# Dislikes: 131
# Total Accepted:    393K
# Total Submissions: 477K
# Testcase Example:  "5"
#
# There are n friends that are playing a game. The friends are sitting in a
# circle and are numbered from 1 to n in clockwise order. More formally, moving
# clockwise from the i^th friend brings you to the (i+1)^th friend for 1 <= i <
# n, and moving clockwise from the n^th friend brings you to the 1^st friend.
#
# The rules of the game are as follows:
#
# Start at the 1^st friend.
#
# Count the next k friends in the clockwise direction including the friend you
# started at. The counting wraps around the circle and may count some friends
# more than once.
#
# The last friend you counted leaves the circle and loses the game.
#
# If there is still more than one friend in the circle, go back to step 2
# starting from the friend immediately clockwise of the friend who just lost
# and repeat.
#
# Else, the last friend in the circle wins the game.
#
# Given the number of friends, n, and an integer k, return the winner of the
# game.
#
# Example 1:
#
# Input: n = 5, k = 2
# Output: 3
# Explanation: Here are the steps of the game:
# 1) Start at friend 1.
# 2) Count 2 friends clockwise, which are friends 1 and 2.
# 3) Friend 2 leaves the circle. Next start is friend 3.
# 4) Count 2 friends clockwise, which are friends 3 and 4.
# 5) Friend 4 leaves the circle. Next start is friend 5.
# 6) Count 2 friends clockwise, which are friends 5 and 1.
# 7) Friend 1 leaves the circle. Next start is friend 3.
# 8) Count 2 friends clockwise, which are friends 3 and 5.
# 9) Friend 5 leaves the circle. Only friend 3 is left, so they are the winner.
#
# Example 2:
#
# Input: n = 6, k = 5
# Output: 1
# Explanation: The friends leave in this order: 5, 4, 6, 2, 3. The winner is
# friend 1.
#
# Constraints:
#
# 1 <= k <= n <= 500
#
# Follow up:
#
# Could you solve this problem in linear time with constant space?
#

# @lc code=start
from collections import deque


class Solution:
    def findTheWinner(self, n: int, k: int) -> int:
        """
        Interview explanation:
        Josephus problem: every k-th friend eliminated in circle until one remains.
        Simulation with queue is classic and clear.

        Algorithm (queue simulation):
        - deque 1..n; while >1: rotate k-1 to back, popleft eliminated.
        - Return last remaining (1-indexed friends).

        Complexity: O(n*k) time, O(n) space.
        """
        q = deque(range(1, n + 1))
        while len(q) > 1:
            q.rotate(1 - k)
            q.popleft()
        return q[0]

    def findTheWinner_math(self, n: int, k: int) -> int:
        """
        Interview explanation:
        Classic O(n) Josephus DP: f(1)=0; f(i)=(f(i-1)+k)%i (0-indexed), +1.

        Algorithm (math recurrence):
        - Iterate i=2..n updating winner index.

        Complexity: O(n) time, O(1) space.
        """
        w = 0
        for i in range(2, n + 1):
            w = (w + k) % i
        return w + 1
# @lc code=end
