#
# @lc app=leetcode id=864 lang=python3
#
# [864] Shortest Path to Get All Keys
#
# https://leetcode.com/problems/shortest-path-to-get-all-keys/description/
#
# algorithms
# Hard (54.87%)
# Likes:    2517
# Dislikes: 107
# Total Accepted:    100K
# Total Submissions: 183K
# Testcase Example:  "[\"@.a..\",\"###.#\",\"b.A.B\"]"
#
# You are given an m x n grid grid where:
#
# '.' is an empty cell.
#
# '#' is a wall.
#
# '@' is the starting point.
#
# Lowercase letters represent keys.
#
# Uppercase letters represent locks.
#
# You start at the starting point and one move consists of walking one space in
# one of the four cardinal directions. You cannot walk outside the grid, or
# walk into a wall.
#
# If you walk over a key, you can pick it up and you cannot walk over a lock
# unless you have its corresponding key.
#
# For some 1 <= k <= 6, there is exactly one lowercase and one uppercase letter
# of the first k letters of the English alphabet in the grid. This means that
# there is exactly one key for each lock, and one lock for each key; and also
# that the letters used to represent the keys and locks were chosen in the same
# order as the English alphabet.
#
# Return the lowest number of moves to acquire all keys. If it is impossible,
# return -1.
#
# Example 1:
#
# Input: grid = ["@.a..","###.#","b.A.B"]
# Output: 8
# Explanation: Note that the goal is to obtain all the keys not to open all the
# locks.
#
# Example 2:
#
# Input: grid = ["@..aA","..B#.","....b"]
# Output: 6
#
# Example 3:
#
# Input: grid = ["@Aa"]
# Output: -1
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 30
#
# grid[i][j] is either an English letter, '.', '#', or '@'.
#
# There is exactly one '@' in the grid.
#
# The number of keys in the grid is in the range [1, 6].
#
# Each key in the grid is unique.
#
# Each key in the grid has a matching lock.
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def shortestPathAllKeys(self, grid: List[str]) -> int:
        """
        Interview explanation:
        Collect all keys; doors need matching keys. State is (r,c,keymask);
        BFS for shortest path in this state graph.

        Algorithm (BFS state):
        - Find start '@' and total keys (lowercase count).
        - BFS (r,c,mask,steps); on key OR bit; on door require bit; visit seen.

        Complexity: O(m*n*2^k) time/space, k=#keys <= 6.
        """
        m, n = len(grid), len(grid[0])
        start = None
        all_keys = 0
        for i in range(m):
            for j in range(n):
                c = grid[i][j]
                if c == "@":
                    start = (i, j)
                elif "a" <= c <= "f":
                    all_keys |= 1 << (ord(c) - ord("a"))
        q = deque([(start[0], start[1], 0, 0)])
        seen = {(start[0], start[1], 0)}
        while q:
            r, c, mask, steps = q.popleft()
            if mask == all_keys:
                return steps
            for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if not (0 <= nr < m and 0 <= nc < n):
                    continue
                ch = grid[nr][nc]
                if ch == "#":
                    continue
                nmask = mask
                if "a" <= ch <= "f":
                    nmask |= 1 << (ord(ch) - ord("a"))
                elif "A" <= ch <= "F":
                    if not (mask & (1 << (ord(ch) - ord("A")))):
                        continue
                state = (nr, nc, nmask)
                if state not in seen:
                    seen.add(state)
                    q.append((nr, nc, nmask, steps + 1))
        return -1
# @lc code=end

