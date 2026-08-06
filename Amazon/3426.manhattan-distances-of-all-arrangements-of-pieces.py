#
# @lc app=leetcode id=3426 lang=python3
#
# [3426] Manhattan Distances of All Arrangements of Pieces
#
# https://leetcode.com/problems/manhattan-distances-of-all-arrangements-of-pieces/description/
#
# algorithms
# Hard (35.85%)
# Likes:    42
# Dislikes: 11
# Total Accepted:    4.1K
# Total Submissions: 11.4K
# Testcase Example:  "2\n2\n2"
#
#
# You are given three integers m, n, and k.
#
# There is a rectangular grid of size m × n containing k identical pieces.
# Return the sum of Manhattan distances between every pair of pieces over
# all valid arrangements of pieces.
#
# A valid arrangement is a placement of all k pieces on the grid with at
# most one piece per cell.
#
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# The Manhattan Distance between two cells (x_i, y_i) and (x_j, y_j) is
# |x_i - x_j| + |y_i - y_j|.
#
# Example 1:
#
# Input: m = 2, n = 2, k = 2
#
# Output: 8
#
# Explanation:
#
# The valid arrangements of pieces on the board are:
#
# In the first 4 arrangements, the Manhattan distance between the two
# pieces is 1.
#
# In the last 2 arrangements, the Manhattan distance between the two
# pieces is 2.
#
# Thus, the total Manhattan distance across all valid arrangements is 1 +
# 1 + 1 + 1 + 2 + 2 = 8.
#
# Example 2:
#
# Input: m = 1, n = 4, k = 3
#
# Output: 20
#
# Explanation:
#
# The valid arrangements of pieces on the board are:
#
# The first and last arrangements have a total Manhattan distance of 1 + 1
# + 2 = 4.
#
# The middle two arrangements have a total Manhattan distance of 1 + 2 + 3
# = 6.
#
# The total Manhattan distance between all pairs of pieces across all
# arrangements is 4 + 6 + 6 + 4 = 20.
#
# Constraints:
#
# 1 <= m, n <= 10^5
#
# 2 <= m * n <= 10^5
#
# 2 <= k <= m * n
#

# @lc code=start
import math


class Solution:
    def distanceSum(self, m: int, n: int, k: int) -> int:
        """
        Interview explanation:
        Sum Manhattan distances over all pairs of cells, each weighted by how many
        ways to place the remaining k-2 pieces on the other cells: C(mn-2, k-2).

        Algorithm:
        - Row contribution: n^2 * sum_{d=1}^{m-1} d*(m-d) = n^2*(m^3-m)/6.
        - Col contribution: m^2*(n^3-n)/6.
        - Multiply by C(m*n-2, k-2) mod 1e9+7.

        Complexity: O(k) for comb (or O(1) with math.comb), O(1) space.
        """
        MOD = 10**9 + 7
        pair_sum = n * n * (m * m * m - m) // 6 + m * m * (n * n * n - n) // 6
        return pair_sum * math.comb(m * n - 2, k - 2) % MOD
# @lc code=end
