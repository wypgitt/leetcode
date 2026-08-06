#
# @lc app=leetcode id=1197 lang=python3
#
# [1197] Minimum Knight Moves
#
# https://leetcode.com/problems/minimum-knight-moves/description/
#
# algorithms
# Medium (42.05%)
# Likes:    1568
# Dislikes: 411
# Total Accepted:    195.7K
# Total Submissions: 465.5K
# Testcase Example:  "2\n1"
#
#
# In an infinite chess board with coordinates from -infinity to +infinity,
# you have a knight at square [0, 0].
#
# A knight has 8 possible moves it can make, as illustrated below. Each
# move is two squares in a cardinal direction, then one square in an
# orthogonal direction.
#
# Return the minimum number of steps needed to move the knight to the
# square [x, y]. It is guaranteed the answer exists.
#
# Example 1:
#
# Input: x = 2, y = 1
# Output: 1
# Explanation: [0, 0] → [2, 1]
#
# Example 2:
#
# Input: x = 5, y = 5
# Output: 4
# Explanation: [0, 0] → [2, 1] → [4, 2] → [3, 4] → [5, 5]
#
# Constraints:
#
# -300 <= x, y <= 300
#
# 0 <= |x| + |y| <= 300
#
# @lc code=start

from collections import deque


class Solution:
    def minKnightMoves(self, x: int, y: int) -> int:
        """
        Interview explanation:
        Premium: knight from (0,0) to (x,y) on an infinite board. By symmetry
        reduce to first quadrant and BFS with knight deltas; prune coordinates
        slightly outside the target box.

        Algorithm (BFS):
        - x,y = abs. Queue (0,0); 8 deltas; visit until (x,y).
        - Bound search to roughly [-2, x+2] x [-2, y+2].

        Complexity: O((|x|+|y|)^2) states worst case, O(same) space.
        """
        x, y = abs(x), abs(y)
        q = deque([(0, 0)])
        seen = {(0, 0)}
        deltas = ((1, 2), (1, -2), (-1, 2), (-1, -2),
                  (2, 1), (2, -1), (-2, 1), (-2, -1))
        steps = 0
        while q:
            for _ in range(len(q)):
                cx, cy = q.popleft()
                if cx == x and cy == y:
                    return steps
                for dx, dy in deltas:
                    nx, ny = cx + dx, cy + dy
                    if (nx, ny) not in seen and -2 <= nx <= x + 2 and -2 <= ny <= y + 2:
                        seen.add((nx, ny))
                        q.append((nx, ny))
            steps += 1
        return -1

    def minKnightMoves_bidirectional(self, x: int, y: int) -> int:
        """
        Interview explanation:
        Alternate: bidirectional BFS from origin and target meeting in the
        middle — fewer expansions on large targets.

        Algorithm:
        - Two frontiers/sets; expand the smaller side each round with knight
          moves (on abs-symmetric coords); when sides intersect, return steps.

        Complexity: Still exponential in distance but ~half depth of one-sided BFS.
        """
        x, y = abs(x), abs(y)
        if x == 0 and y == 0:
            return 0
        deltas = ((1, 2), (1, -2), (-1, 2), (-1, -2),
                  (2, 1), (2, -1), (-2, 1), (-2, -1))
        front = {(0, 0)}
        back = {(x, y)}
        seen_f = {(0, 0)}
        seen_b = {(x, y)}
        steps = 0
        while front and back:
            if len(front) > len(back):
                front, back = back, front
                seen_f, seen_b = seen_b, seen_f
            steps += 1
            nxt = set()
            for cx, cy in front:
                for dx, dy in deltas:
                    nx, ny = cx + dx, cy + dy
                    if (nx, ny) in seen_b:
                        return steps
                    if (nx, ny) not in seen_f and -2 <= nx <= x + 2 and -2 <= ny <= y + 2:
                        seen_f.add((nx, ny))
                        nxt.add((nx, ny))
            front = nxt
        return -1
# @lc code=end
