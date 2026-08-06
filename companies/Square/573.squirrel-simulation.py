#
# @lc app=leetcode id=573 lang=python3
#
# [573] Squirrel Simulation
#
# https://leetcode.com/problems/squirrel-simulation/description/
#
# algorithms
# Medium (57.37%)
# Likes:    421
# Dislikes: 40
# Total Accepted:    24.3K
# Total Submissions: 42.3K
# Testcase Example:  "5\n7\n[2,2]\n[4,4]\n[[3,0], [2,5]]"
#
#
# You are given two integers height and width representing a garden of
# size height x width. You are also given:
#
# an array tree where tree = [tree_r, tree_c] is the position of the tree
# in the garden,
#
# an array squirrel where squirrel = [squirrel_r, squirrel_c] is the
# position of the squirrel in the garden,
#
# and an array nuts where nuts[i] = [nut_i_r, nut_i_c] is the position of
# the i^th nut in the garden.
#
# The squirrel can only take at most one nut at one time and can move in
# four directions: up, down, left, and right, to the adjacent cell.
#
# Return the minimal distance for the squirrel to collect all the nuts and
# put them under the tree one by one.
#
# The distance is the number of moves.
#
# Example 1:
#
# Input: height = 5, width = 7, tree = [2,2], squirrel = [4,4], nuts =
# [[3,0], [2,5]]
# Output: 12
# Explanation: The squirrel should go to the nut at [2, 5] first to
# achieve a minimal distance.
#
# Example 2:
#
# Input: height = 1, width = 3, tree = [0,1], squirrel = [0,0], nuts =
# [[0,2]]
# Output: 3
#
# Constraints:
#
# 1 <= height, width <= 100
#
# tree.length == 2
#
# squirrel.length == 2
#
# 1 <= nuts.length <= 5000
#
# nuts[i].length == 2
#
# 0 <= tree_r, squirrel_r, nut_i_r <= height
#
# 0 <= tree_c, squirrel_c, nut_i_c <= width
#
# @lc code=start
from typing import List


class Solution:
    def minDistance(
        self,
        height: int,
        width: int,
        tree: List[int],
        squirrel: List[int],
        nuts: List[List[int]],
    ) -> int:
        """
        Interview explanation:
        Premium geometry/greedy: every nut must go tree→nut→tree except the
        first trip which is squirrel→firstNut→tree. Total distance is
        2*Σ dist(tree, nut) minus the maximum savings from choosing the first
        nut: dist(tree, nut) - dist(squirrel, nut).

        Algorithm:
        - Manhattandist(a,b) = |ax-bx| + |ay-by|.
        - total = 2 * sum(dist(tree, nut) for nut in nuts).
        - Save max over nuts of dist(tree, nut) - dist(squirrel, nut).
        - Answer = total - save.

        Complexity: O(#nuts) time, O(1) space.
        """
        def dist(a: List[int], b: List[int]) -> int:
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        total = 0
        save = float("-inf")
        for nut in nuts:
            d_tree = dist(tree, nut)
            total += 2 * d_tree
            save = max(save, d_tree - dist(squirrel, nut))
        return total - save
# @lc code=end

