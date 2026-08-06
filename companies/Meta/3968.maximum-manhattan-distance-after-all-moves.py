#
# @lc app=leetcode id=3968 lang=python3
#
# [3968] Maximum Manhattan Distance After All Moves
#
# https://leetcode.com/problems/maximum-manhattan-distance-after-all-moves/description/
#
# algorithms
# Medium (63.61%)
# Likes:    46
# Dislikes: 3
# Total Accepted:    46.7K
# Total Submissions: 73.3K
# Testcase Example:  "\"L_D_\""
#
#
# You are given a string moves consisting of the characters 'U', 'D', 'L',
# 'R', and '_'.
#
# Starting from the origin (0, 0), each character represents one move on a
# 2D plane:
#
# 'U': Move up by 1 unit.
#
# 'D': Move down by 1 unit.
#
# 'L': Move left by 1 unit.
#
# 'R': Move right by 1 unit.
#
# '_': Can be independently replaced with any one of 'U', 'D', 'L', or
# 'R'.
#
# Return the maximum Manhattan distance from the origin that can be
# achieved after all moves have been performed.
#
# Example 1:
#
# Input: moves = "L_D_"
#
# Output: 4
#
# Explanation:
#
# One optimal choice is:
#
# 'L': (0, 0) -> (-1, 0)
#
# '_' treated as 'D': (-1, 0) -> (-1, -1)
#
# 'D': (-1, -1) -> (-1, -2)
#
# '_' treated as 'L': (-1, -2) -> (-2, -2)
#
# The final Manhattan distance from the origin is |0 - (-2)| + |0 - (-2)|
# = 4.
#
# Example 2:
#
# Input: moves = "U_R"
#
# Output: 3
#
# Explanation:
#
# One optimal choice is:
#
# 'U': (0, 0) -> (0, 1)
#
# '_' treated as 'U': (0, 1) -> (0, 2)
#
# 'R': (0, 2) -> (1, 2)
#
# The final Manhattan distance from the origin is |0 - 1| + |0 - 2| = 3.
#
# Constraints:
#
# 1 <= moves.length <= 10^5
#
# moves consists of only 'U', 'D', 'L', 'R', and '_'.
#

# @lc code=start

class Solution:
    def maxDistance(self, moves: str) -> int:
        """
        Interview explanation:
        Fixed moves set the net (dx, dy); every '_' can extend Manhattan distance
        by 1 in the optimal direction.

        Algorithm:
        - Accumulate net vertical and horizontal displacement from U/D/L/R.
        - Count wildcards '_'.
        - Answer = |dx| + |dy| + wildcards.

        Complexity: O(n) time, O(1) space.
        """
        x = y = z = 0
        for c in moves:
            if c == "U":
                x -= 1
            elif c == "D":
                x += 1
            elif c == "L":
                y -= 1
            elif c == "R":
                y += 1
            else:
                z += 1
        return abs(x) + abs(y) + z
# @lc code=end
