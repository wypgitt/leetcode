#
# @lc app=leetcode id=2849 lang=python3
#
# [2849] Determine if a Cell Is Reachable at a Given Time
#
# https://leetcode.com/problems/determine-if-a-cell-is-reachable-at-a-given-time/description/
#
# algorithms
# Medium (37.47%)
# Likes:    843
# Dislikes: 773
# Total Accepted:    113K
# Total Submissions: 301.6K
# Testcase Example:  "2\n4\n7\n7\n6"
#
#
# You are given four integers sx, sy, fx, fy, and a non-negative integer
# t.
#
# In an infinite 2D grid, you start at the cell (sx, sy). Each second, you
# must move to any of its adjacent cells.
#
# Return true if you can reach cell (fx, fy) after exactly t seconds, or
# false otherwise.
#
# A cell's adjacent cells are the 8 cells around it that share at least
# one corner with it. You can visit the same cell several times.
#
# Example 1:
#
# Input: sx = 2, sy = 4, fx = 7, fy = 7, t = 6
# Output: true
# Explanation: Starting at cell (2, 4), we can reach cell (7, 7) in
# exactly 6 seconds by going through the cells depicted in the picture
# above.
#
# Example 2:
#
# Input: sx = 3, sy = 1, fx = 7, fy = 3, t = 3
# Output: false
# Explanation: Starting at cell (3, 1), it takes at least 4 seconds to
# reach cell (7, 3) by going through the cells depicted in the picture
# above. Hence, we cannot reach cell (7, 3) at the third second.
#
# Constraints:
#
# 1 <= sx, sy, fx, fy <= 10^9
#
# 0 <= t <= 10^9
#

# @lc code=start
class Solution:
    def isReachableAtTime(self, sx: int, sy: int, fx: int, fy: int, t: int) -> bool:
        """
        Interview explanation:
        8-direction moves each second (Chebyshev). Reach (fx,fy) in exactly t seconds.

        Algorithm:
        - Need t >= max(|dx|, |dy|).
        - Same cell: t == 0 ok; t == 1 impossible (must move); t >= 2 ok (leave and return).

        Complexity: O(1) time and space.
        """
        if sx == fx and sy == fy:
            return t != 1
        return t >= max(abs(sx - fx), abs(sy - fy))
# @lc code=end
