#
# @lc app=leetcode id=3609 lang=python3
#
# [3609] Minimum Moves to Reach Target in Grid
#
# https://leetcode.com/problems/minimum-moves-to-reach-target-in-grid/description/
#
# algorithms
# Hard (15.40%)
# Likes:    57
# Dislikes: 3
# Total Accepted:    5.5K
# Total Submissions: 35.6K
# Testcase Example:  "1\n2\n5\n4"
#
#
# You are given four integers sx, sy, tx, and ty, representing two points
# (sx, sy) and (tx, ty) on an infinitely large 2D grid.
#
# You start at (sx, sy).
#
# At any point (x, y), define m = max(x, y). You can either:
#
# Move to (x + m, y), or
#
# Move to (x, y + m).
#
# Return the minimum number of moves required to reach (tx, ty). If it is
# impossible to reach the target, return -1.
#
# Example 1:
#
# Input: sx = 1, sy = 2, tx = 5, ty = 4
#
# Output: 2
#
# Explanation:
#
# The optimal path is:
#
# Move 1: max(1, 2) = 2. Increase the y-coordinate by 2, moving from (1,
# 2) to (1, 2 + 2) = (1, 4).
#
# Move 2: max(1, 4) = 4. Increase the x-coordinate by 4, moving from (1,
# 4) to (1 + 4, 4) = (5, 4).
#
# Thus, the minimum number of moves to reach (5, 4) is 2.
#
# Example 2:
#
# Input: sx = 0, sy = 1, tx = 2, ty = 3
#
# Output: 3
#
# Explanation:
#
# The optimal path is:
#
# Move 1: max(0, 1) = 1. Increase the x-coordinate by 1, moving from (0,
# 1) to (0 + 1, 1) = (1, 1).
#
# Move 2: max(1, 1) = 1. Increase the x-coordinate by 1, moving from (1,
# 1) to (1 + 1, 1) = (2, 1).
#
# Move 3: max(2, 1) = 2. Increase the y-coordinate by 2, moving from (2,
# 1) to (2, 1 + 2) = (2, 3).
#
# Thus, the minimum number of moves to reach (2, 3) is 3.
#
# Example 3:
#
# Input: sx = 1, sy = 1, tx = 2, ty = 2
#
# Output: -1
#
# Explanation:
#
# It is impossible to reach (2, 2) from (1, 1) using the allowed moves.
# Thus, the answer is -1.
#
# Constraints:
#
# 0 <= sx <= tx <= 10^9
#
# 0 <= sy <= ty <= 10^9
#

# @lc code=start

class Solution:
    def minMoves(self, sx: int, sy: int, tx: int, ty: int) -> int:
        """
        Interview explanation:
        From (x,y) you may add m=max(x,y) to one coordinate. Work backward
        from the target: undo the unique feasible last move greedily.

        Algorithm:
        - While (tx,ty) ≠ (sx,sy): if below start, impossible.
        - If tx > ty: either tx -= ty (when previous max was ty) or tx //= 2
          (when previous max was tx/2 and tx even); symmetric for ty > tx.
        - If equal: only undo via a zero start coordinate.

        Complexity: O(log tx + log ty) time, O(1) space.
        """
        moves = 0
        while (sx, sy) != (tx, ty):
            if sx > tx or sy > ty:
                return -1
            if tx < ty:
                if tx > ty - tx:
                    ty -= tx
                else:
                    if ty % 2:
                        return -1
                    ty -= ty // 2
            elif tx > ty:
                if ty > tx - ty:
                    tx -= ty
                else:
                    if tx % 2:
                        return -1
                    tx -= tx // 2
            else:
                if sx == 0:
                    tx -= ty
                elif sy == 0:
                    ty -= tx
                else:
                    return -1
            moves += 1
        return moves
# @lc code=end
