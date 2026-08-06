#
# @lc app=leetcode id=3694 lang=python3
#
# [3694] Distinct Points Reachable After Substring Removal
#
# https://leetcode.com/problems/distinct-points-reachable-after-substring-removal/description/
#
# algorithms
# Medium (53.33%)
# Likes:    67
# Dislikes: 1
# Total Accepted:    17.3K
# Total Submissions: 32.4K
# Testcase Example:  "\"LUL\"\n1"
#
#
# You are given a string s consisting of characters 'U', 'D', 'L', and
# 'R', representing moves on an infinite 2D Cartesian grid.
#
# 'U': Move from (x, y) to (x, y + 1).
#
# 'D': Move from (x, y) to (x, y - 1).
#
# 'L': Move from (x, y) to (x - 1, y).
#
# 'R': Move from (x, y) to (x + 1, y).
#
# You are also given a positive integer k.
#
# You must choose and remove exactly one contiguous substring of length k
# from s. Then, start from coordinate (0, 0) and perform the remaining
# moves in order.
#
# Return an integer denoting the number of distinct final coordinates
# reachable.
#
# Example 1:
#
# Input: s = "LUL", k = 1
#
# Output: 2
#
# Explanation:
#
# After removing a substring of length 1, s can be "UL", "LL" or "LU".
# Following these moves, the final coordinates will be (-1, 1), (-2, 0)
# and (-1, 1) respectively. There are two distinct points (-1, 1) and (-2,
# 0) so the answer is 2.
#
# Example 2:
#
# Input: s = "UDLR", k = 4
#
# Output: 1
#
# Explanation:
#
# After removing a substring of length 4, s can only be the empty string.
# The final coordinates will be (0, 0). There is only one distinct point
# (0, 0) so the answer is 1.
#
# Example 3:
#
# Input: s = "UU", k = 1
#
# Output: 1
#
# Explanation:
#
# After removing a substring of length 1, s becomes "U", which always ends
# at (0, 1), so there is only one distinct final coordinate.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists of only 'U', 'D', 'L', and 'R'.
#
# 1 <= k <= s.length
#

# @lc code=start

class Solution:
    def distinctPoints(self, s: str, k: int) -> int:
        """
        Interview explanation:
        Final position = total displacement minus the removed window's
        displacement, so distinct finals ↔ distinct length-k window moves.

        Algorithm:
        - Prefix positions; for each window [i, i+k) record
          (total_x - dx, total_y - dy) in a set.

        Complexity: O(n) time, O(n) space.
        """
        n = len(s)
        move = {'U': (0, 1), 'D': (0, -1), 'L': (-1, 0), 'R': (1, 0)}
        px = [0] * (n + 1)
        py = [0] * (n + 1)
        for i, c in enumerate(s):
            dx, dy = move[c]
            px[i + 1] = px[i] + dx
            py[i + 1] = py[i] + dy
        seen = set()
        tx, ty = px[n], py[n]
        for i in range(n - k + 1):
            seen.add((tx - (px[i + k] - px[i]), ty - (py[i + k] - py[i])))
        return len(seen)
# @lc code=end
