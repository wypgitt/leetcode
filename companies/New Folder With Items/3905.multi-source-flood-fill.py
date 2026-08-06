#
# @lc app=leetcode id=3905 lang=python3
#
# [3905] Multi Source Flood Fill
#
#
# --- Interview Notes ---------------------------------------------------------
#
# Problem restatement
# We are given an n by m grid. Some cells are initially colored:
#
#   sources[i] = [row, col, color]
#
# All other cells start uncolored as 0.
#
# At every time step, all currently colored cells simultaneously spread their
# color to adjacent uncolored cells in the four directions.
#
# If multiple colors reach the same uncolored cell at the same time step, that
# cell takes the maximum color value among them.
#
# Return the final colored grid.
#
#
# Graph interpretation
# Treat every grid cell as a graph node.
# Adjacent cells are connected by unit-weight edges.
#
# A source colors itself at distance/time 0.
# Every other cell is colored at the minimum Manhattan/grid distance from any
# source.
#
# If several sources reach a cell at that same minimum distance, the largest
# color wins.
#
# This is exactly a multi-source BFS problem with a tie rule.
#
#
# Important detail: simultaneous spreading
# If we color a cell immediately when the first neighbor reaches it, we might
# miss another neighbor reaching it in the same time step with a larger color.
#
# Example:
#   a cell can be reached from color 1 and color 5 at time 3.
#   It must become 5, not whichever BFS neighbor happens to be processed first.
#
# Therefore, process BFS one level at a time:
#   1. current frontier contains cells colored at time t
#   2. collect proposals for uncolored neighbors at time t + 1
#   3. if multiple proposals target the same cell, keep the max color
#   4. after all current frontier cells are processed, assign the proposals
#
#
# Data structure choice
#
# 1. grid
#    Stores the final/current color of each cell.
#
# 2. dist
#    dist[r][c] = time when the cell was colored, or -1 if uncolored.
#    This prevents a later wave from overwriting a cell that was already reached
#    earlier.
#
# 3. deque frontier
#    Standard BFS queue of cells colored at the current/next levels.
#
# 4. proposals dictionary
#    For one BFS layer, maps:
#      flattened_cell_index -> best color proposed for that cell
#
#    Flattening (r, c) as r*m + c makes dictionary keys compact.
#
#
# Algorithm
# 1. Initialize grid and dist.
# 2. Put every source into the BFS queue with dist = 0.
# 3. While the queue is not empty:
#      - process exactly the current queue length as one time layer
#      - for every neighbor that is still uncolored:
#          proposals[neighbor] = max(proposals[neighbor], current_color)
#      - after the layer, color every proposed cell and append it to the queue
# 4. Return grid.
#
#
# Why this computes the right color
# BFS explores cells in increasing distance from the nearest source.
# The first time a cell is assigned, that layer is its minimum possible time.
# Because all proposals within the layer are combined before assignment, ties at
# that minimum time are resolved by maximum color.
#
#
# Correctness proof
#
# Lemma 1: BFS layer t contains exactly cells colored at time t.
# Proof:
# Sources are initialized at time 0. If the invariant holds for time t, then
# the only cells that can first be colored at time t+1 are uncolored neighbors
# of time-t cells. The algorithm collects exactly those neighbors as proposals
# and assigns them after the layer. Thus the invariant holds by induction.
#
# Lemma 2: A cell is assigned at its minimum distance from any source.
# Proof:
# By Lemma 1, BFS processes layers in increasing time. A cell is assigned only
# when it is first proposed from the previous layer. If it could be reached
# earlier, it would have been proposed and assigned in an earlier layer.
#
# Lemma 3: If multiple colors reach a cell at its minimum time, the algorithm
# assigns the maximum of those colors.
# Proof:
# All spreads from time t to time t+1 are collected in the same proposals
# dictionary before any proposed cell is finalized. For each cell, the dictionary
# stores the maximum proposed color. Therefore all simultaneous arrivals are
# considered and the largest color is chosen.
#
# Theorem: The algorithm returns the final grid described by the process.
# Proof:
# By Lemma 2, every cell is colored at the correct earliest time. By Lemma 3,
# ties at that time are resolved by maximum color. Once a cell is colored, later
# waves cannot change it because the process only spreads to uncolored cells.
# This matches the problem exactly.
#
#
# Complexity analysis
#
# Let N = n * m.
#
# Time:
#   Each cell is colored once.
#   Each colored cell checks up to 4 neighbors.
#   Dictionary proposal work is proportional to neighbor checks.
#   Overall time complexity: O(N).
#
# Space:
#   grid and dist use O(N).
#   The queue and proposals can hold O(N) cells in the worst case.
#   Overall space complexity: O(N).
#
#
# Tests to discuss in an interview
#
# 1. Example 1:
#      n = 3, m = 3, sources = [[0,0,1],[2,2,2]]
#      Tie cells choose color 2.
#
# 2. Example 2:
#      Adjacent sources with different colors.
#
# 3. Single source:
#      Every cell receives that source color.
#
# 4. All cells are sources:
#      No spreading is needed; output equals initial source colors.
#
# 5. Tie among more than two colors:
#      The max color among all simultaneous arrivals should win.
#
#
# Edge cases
#
# - n*m can be 1e5, so recursion is unnecessary and BFS is safe.
# - sources positions are distinct, so no initial tie at time 0.
# - A later larger color must not overwrite an earlier smaller color, because
#   only simultaneous arrivals tie-break.
#
#
# Possible improvements
#
# - A priority queue ordered by (distance, -color) can also solve this, but BFS
#   layer batching is simpler and strictly linear for unit edges.
# - We could omit dist and use grid == 0 as the uncolored marker because source
#   colors are positive. Keeping dist makes the time/distance invariant explicit.
#
# -------------------------------------------------------------------------------

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def colorGrid(self, n: int, m: int, sources: List[List[int]]) -> List[List[int]]:
        grid = [[0] * m for _ in range(n)]
        dist = [[-1] * m for _ in range(n)]
        queue = deque()

        for row, col, color in sources:
            grid[row][col] = color
            dist[row][col] = 0
            queue.append((row, col))

        directions = ((1, 0), (-1, 0), (0, 1), (0, -1))
        time = 0

        while queue:
            proposals = {}

            for _ in range(len(queue)):
                row, col = queue.popleft()
                color = grid[row][col]

                for dr, dc in directions:
                    nr = row + dr
                    nc = col + dc
                    if 0 <= nr < n and 0 <= nc < m and dist[nr][nc] == -1:
                        key = nr * m + nc
                        if color > proposals.get(key, 0):
                            proposals[key] = color

            time += 1
            for key, color in proposals.items():
                row, col = divmod(key, m)
                if dist[row][col] == -1:
                    dist[row][col] = time
                    grid[row][col] = color
                    queue.append((row, col))

        return grid


# @lc code=end
