#
# @lc app=leetcode id=780 lang=python3
#
# [780] Reaching Points
#
# https://leetcode.com/problems/reaching-points/description/
#
# algorithms
# Hard (34.53%)
# Likes:    1597
# Dislikes: 239
# Total Accepted:    83.4K
# Total Submissions: 242K
# Testcase Example:  "1"
#
# Given four integers sx, sy, tx, and ty, return true if it is possible to
# convert the point (sx, sy) to the point (tx, ty) through some operations, or
# false otherwise.
#
# The allowed operation on some point (x, y) is to convert it to either (x, x +
# y) or (x + y, y).
#
# Example 1:
#
# Input: sx = 1, sy = 1, tx = 3, ty = 5
# Output: true
# Explanation:
# One series of moves that transforms the starting point to the target is:
# (1, 1) -> (1, 2)
# (1, 2) -> (3, 2)
# (3, 2) -> (3, 5)
#
# Example 2:
#
# Input: sx = 1, sy = 1, tx = 2, ty = 2
# Output: false
#
# Example 3:
#
# Input: sx = 1, sy = 1, tx = 1, ty = 1
# Output: true
#
# Constraints:
#
# 1 <= sx, sy, tx, ty <= 10^9
#

# @lc code=start
class Solution:
    def reachingPoints(self, sx: int, sy: int, tx: int, ty: int) -> bool:
        """
        Interview explanation:
        Forward (x,y)→(x+y,y) or (x,x+y) explodes. Work backwards: while
        tx > sx and ty > sy, replace the larger by larger % smaller (since
        subtracting the smaller repeatedly is modulo). Then check if we can
        reduce the remaining axis to match by subtracting multiples.

        Algorithm:
        - While tx > sx and ty > sy:
            if tx > ty: tx %= ty else ty %= tx
        - If tx == sx and ty >= sy and (ty - sy) % sx == 0: True
        - If ty == sy and tx >= sx and (tx - sx) % sy == 0: True
        - Else False

        Complexity: O(log(max(tx, ty))) time, O(1) space.
        """
        while tx > sx and ty > sy:
            if tx > ty:
                tx %= ty
            else:
                ty %= tx
        if tx == sx and ty >= sy and (ty - sy) % sx == 0:
            return True
        if ty == sy and tx >= sx and (tx - sx) % sy == 0:
            return True
        return False
# @lc code=end

