#
# @lc app=leetcode id=488 lang=python3
#
# [488] Zuma Game
#
# https://leetcode.com/problems/zuma-game/description/
#
# algorithms
# Hard (29.43%)
# Likes:    499
# Dislikes: 516
# Total Accepted:    31.0K
# Total Submissions: 105K
# Testcase Example:  "\"WRRBBW\""
#
# You are playing a variation of the game Zuma.
#
# In this variation of Zuma, there is a single row of colored balls on a board,
# where each ball can be colored red 'R', yellow 'Y', blue 'B', green 'G', or
# white 'W'. You also have several colored balls in your hand.
#
# Your goal is to clear all of the balls from the board. On each turn:
#
# Pick any ball from your hand and insert it in between two balls in the row or
# on either end of the row.
#
# If there is a group of three or more consecutive balls of the same color,
# remove the group of balls from the board.
#
# If this removal causes more groups of three or more of the same color to
# form, then continue removing each group until there are none left.
#
# If there are no more balls on the board, then you win the game.
#
# Repeat this process until you either win or do not have any more balls in
# your hand.
#
# Given a string board, representing the row of balls on the board, and a
# string hand, representing the balls in your hand, return the minimum number
# of balls you have to insert to clear all the balls from the board. If you
# cannot clear all the balls from the board using the balls in your hand,
# return -1.
#
# Example 1:
#
# Input: board = "WRRBBW", hand = "RB"
# Output: -1
# Explanation: It is impossible to clear all the balls. The best you can do is:
# - Insert 'R' so the board becomes WRRRBBW. WRRRBBW -> WBBW.
# - Insert 'B' so the board becomes WBBBW. WBBBW -> WW.
# There are still balls remaining on the board, and you are out of balls to
# insert.
#
# Example 2:
#
# Input: board = "WWRRBBWW", hand = "WRBRW"
# Output: 2
# Explanation: To make the board empty:
# - Insert 'R' so the board becomes WWRRRBBWW. WWRRRBBWW -> WWBBWW.
# - Insert 'B' so the board becomes WWBBBWW. WWBBBWW -> WWWW -> empty.
# 2 balls from your hand were needed to clear the board.
#
# Example 3:
#
# Input: board = "G", hand = "GGGGG"
# Output: 2
# Explanation: To make the board empty:
# - Insert 'G' so the board becomes GG.
# - Insert 'G' so the board becomes GGG. GGG -> empty.
# 2 balls from your hand were needed to clear the board.
#
# Constraints:
#
# 1 <= board.length <= 16
#
# 1 <= hand.length <= 5
#
# board and hand consist of the characters 'R', 'Y', 'B', 'G', and 'W'.
#
# The initial row of balls on the board will not have any groups of three or
# more consecutive balls of the same color.
#

# @lc code=start
from collections import Counter
from functools import lru_cache


class Solution:
    def findMinStep(self, board: str, hand: str) -> int:
        """
        Interview explanation:
        Search minimum hand balls to clear the board. Collapse runs of ≥3 same
        color after each insert. DFS + memo over (board, hand multiset); at each
        state insert a hand ball next to a same-color group (optimal prune).

        Algorithm:
        - clean(s): repeatedly remove contiguous runs of length ≥ 3.
        - DFS(board, hand): if board empty return 0; for each color in hand,
          for each run of that color on board, insert enough (or 1) balls,
          recurse; take min steps.
        - Return -1 if impossible.

        Complexity: Exponential in |hand| (≤5); memoized, O(states) space.
        """

        def clean(s: str) -> str:
            while True:
                n = len(s)
                parts = []
                i = 0
                changed = False
                while i < n:
                    j = i + 1
                    while j < n and s[j] == s[i]:
                        j += 1
                    if j - i < 3:
                        parts.append(s[i:j])
                    else:
                        changed = True
                    i = j
                s = "".join(parts)
                if not changed:
                    return s

        @lru_cache(None)
        def dfs(b: str, h: str) -> int:
            if not b:
                return 0
            hc = Counter(h)
            ans = float("inf")
            i = 0
            while i < len(b):
                j = i
                while j < len(b) and b[j] == b[i]:
                    j += 1
                color = b[i]
                need = 3 - (j - i)
                if need < 0:
                    need = 0
                if hc[color] >= need and need > 0:
                    hc[color] -= need
                    nh = "".join(sorted(hc.elements()))
                    res = dfs(clean(b[:i] + b[j:]), nh)
                    if res >= 0:
                        ans = min(ans, need + res)
                    hc[color] += need
                i = j
            return int(ans) if ans < float("inf") else -1

        return dfs(board, "".join(sorted(hand)))
# @lc code=end
