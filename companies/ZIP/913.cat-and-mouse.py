#
# @lc app=leetcode id=913 lang=python3
#
# [913] Cat and Mouse
#
# https://leetcode.com/problems/cat-and-mouse/description/
#
# algorithms
# Hard (35.74%)
# Likes:    1031
# Dislikes: 182
# Total Accepted:    29.3K
# Total Submissions: 82.0K
# Testcase Example:  "[[2,5],[3],[0,4,5],[1,4,5],[2,3],[0,2,3]]"
#
# A game on an undirected graph is played by two players, Mouse and Cat, who
# alternate turns.
#
# The graph is given as follows: graph[a] is a list of all nodes b such that ab
# is an edge of the graph.
#
# The mouse starts at node 1 and goes first, the cat starts at node 2 and goes
# second, and there is a hole at node 0.
#
# During each player's turn, they must travel along one edge of the graph that
# meets where they are. For example, if the Mouse is at node 1, it must travel
# to any node in graph[1].
#
# Additionally, it is not allowed for the Cat to travel to the Hole (node 0).
#
# Then, the game can end in three ways:
#
# If ever the Cat occupies the same node as the Mouse, the Cat wins.
#
# If ever the Mouse reaches the Hole, the Mouse wins.
#
# If ever a position is repeated (i.e., the players are in the same position as
# a previous turn, and it is the same player's turn to move), the game is a
# draw.
#
# Given a graph, and assuming both players play optimally, return
#
# 1 if the mouse wins the game,
#
# 2 if the cat wins the game, or
#
# 0 if the game is a draw.
#
# Example 1:
#
# Input: graph = [[2,5],[3],[0,4,5],[1,4,5],[2,3],[0,2,3]]
# Output: 0
#
# Example 2:
#
# Input: graph = [[1,3],[0],[3],[0,2]]
# Output: 1
#
# Constraints:
#
# 3 <= graph.length <= 50
#
# 1 <= graph[i].length < graph.length
#
# 0 <= graph[i][j] < graph.length
#
# graph[i][j] != i
#
# graph[i] is unique.
#
# The mouse and the cat can always move.
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def catMouseGame(self, graph: List[List[int]]) -> int:
        """
        Interview explanation:
        Turn-based game on graph: mouse starts at 1, cat at 2, hole at 0.
        Mouse wins at hole; cat wins by occupying mouse's node; draw if cycles.
        Resolve states via DP/color propagation from terminals (reverse graph).

        Algorithm (DP game):
        - State (m, c, t) t=0 mouse turn / 1 cat turn; result 0/1/2 = draw/mouse/cat.
        - Seed: m==0 → mouse; m==c≠0 → cat.
        - Propagate: if a player can move to their winning state, mark win; if
          all moves lose, mark loss. Cat cannot move to node 0.

        Complexity: O(n^3) time/space.
        """
        n = len(graph)
        DRAW, MOUSE_WIN, CAT_WIN = 0, 1, 2
        # color[m][c][t]
        color = [[[DRAW] * 2 for _ in range(n)] for _ in range(n)]
        degree = [[[0] * 2 for _ in range(n)] for _ in range(n)]

        for m in range(n):
            for c in range(n):
                degree[m][c][0] = len(graph[m])
                degree[m][c][1] = sum(1 for x in graph[c] if x != 0)

        q = deque()
        for t in range(2):
            for i in range(n):
                # mouse at hole
                color[0][i][t] = MOUSE_WIN
                q.append((0, i, t, MOUSE_WIN))
                if i > 0:
                    color[i][i][t] = CAT_WIN
                    q.append((i, i, t, CAT_WIN))

        def parents(m, c, t):
            # states that can move to (m,c,t)
            if t == 0:
                # arrived by cat move from (m, c2, 1)
                for c2 in graph[c]:
                    if c2 != 0:
                        yield (m, c2, 1)
            else:
                # arrived by mouse move from (m2, c, 0)
                for m2 in graph[m]:
                    yield (m2, c, 0)

        while q:
            m, c, t, res = q.popleft()
            for m2, c2, t2 in parents(m, c, t):
                if color[m2][c2][t2] != DRAW:
                    continue
                # player to move at (m2,c2,t2) is mouse if t2==0 else cat
                if (t2 == 0 and res == MOUSE_WIN) or (t2 == 1 and res == CAT_WIN):
                    color[m2][c2][t2] = res
                    q.append((m2, c2, t2, res))
                else:
                    degree[m2][c2][t2] -= 1
                    if degree[m2][c2][t2] == 0:
                        color[m2][c2][t2] = res
                        q.append((m2, c2, t2, res))

        return color[1][2][0]
# @lc code=end
