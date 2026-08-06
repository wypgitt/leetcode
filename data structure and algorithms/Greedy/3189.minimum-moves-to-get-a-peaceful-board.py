#
# @lc app=leetcode id=3189 lang=python3
#
# [3189] Minimum Moves to Get a Peaceful Board
#
# https://leetcode.com/problems/minimum-moves-to-get-a-peaceful-board/description/
#
# algorithms
# Medium (75.66%)
# Likes:    61
# Dislikes: 13
# Total Accepted:    4.9K
# Total Submissions: 6.4K
# Testcase Example:  "[[0,0],[1,0],[1,1]]"
#
#
# Given a 2D array rooks of length n, where rooks[i] = [x_i, y_i]
# indicates the position of a rook on an n x n chess board. Your task is
# to move the rooks 1 cell at a time vertically or horizontally (to an
# adjacent cell) such that the board becomes peaceful.
#
# A board is peaceful if there is exactly one rook in each row and each
# column.
#
# Return the minimum number of moves required to get a peaceful board.
#
# Note that at no point can there be two rooks in the same cell.
#
# Example 1:
#
# Input: rooks = [[0,0],[1,0],[1,1]]
#
# Output: 3
#
# Explanation:
#
# Example 2:
#
# Input: rooks = [[0,0],[0,1],[0,2],[0,3]]
#
# Output: 6
#
# Explanation:
#
# Constraints:
#
# 1 <= n == rooks.length <= 500
#
# 0 <= x_i, y_i <= n - 1
#
# The input is generated such that there are no 2 rooks in the same cell.
#

# @lc code=start

from typing import List


class Solution:
    def minMoves(self, rooks: List[List[int]]) -> int:
        """
        Interview explanation:
        Place n rooks onto distinct rows and columns (like a permutation).
        Row moves and column moves separate; min L1 assignment is sorting.

        Algorithm:
        - Sort by row; sum |row_i - i|. Sort by col; sum |col_j - j|. Add both.

        Complexity: O(n log n) time, O(1) extra space (aside from sort).
        """
        rooks.sort()
        ans = sum(abs(x - i) for i, (x, _) in enumerate(rooks))
        rooks.sort(key=lambda p: p[1])
        ans += sum(abs(y - j) for j, (_, y) in enumerate(rooks))
        return ans

    def minMoves_extract(self, rooks: List[List[int]]) -> int:
        """
        Interview explanation:
        Equivalent: independently match sorted row coordinates to 0..n-1 and
        sorted column coordinates to 0..n-1.

        Algorithm:
        - rows = sorted(x); cols = sorted(y); sum |rows[i]-i| + |cols[i]-i|.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(rooks)
        rows = sorted(x for x, _ in rooks)
        cols = sorted(y for _, y in rooks)
        return sum(abs(rows[i] - i) + abs(cols[i] - i) for i in range(n))
# @lc code=end
