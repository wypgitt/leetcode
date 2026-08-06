#
# @lc app=leetcode id=3648 lang=python3
#
# [3648] Minimum Sensors to Cover Grid
#
# https://leetcode.com/problems/minimum-sensors-to-cover-grid/description/
#
# algorithms
# Medium (68.85%)
# Likes:    54
# Dislikes: 9
# Total Accepted:    30.1K
# Total Submissions: 43.8K
# Testcase Example:  "5\n5\n1"
#
#
# You are given n × m grid and an integer k.
#
# A sensor placed on cell (r, c) covers all cells whose Chebyshev distance
# from (r, c) is at most k.
#
# The Chebyshev distance between two cells (r_1, c_1) and (r_2, c_2) is
# max(|r_1 − r_2|,|c_1 − c_2|).
#
# Your task is to return the minimum number of sensors required to cover
# every cell of the grid.
#
# Example 1:
#
# Input: n = 5, m = 5, k = 1
#
# Output: 4
#
# Explanation:
#
# Placing sensors at positions (0, 3), (1, 0), (3, 3), and (4, 1) ensures
# every cell in the grid is covered. Thus, the answer is 4.
#
# Example 2:
#
# Input: n = 2, m = 2, k = 2
#
# Output: 1
#
# Explanation:
#
# With k = 2, a single sensor can cover the entire 2 * 2 grid regardless
# of its position. Thus, the answer is 1.
#
# Constraints:
#
# 1 <= n <= 10^3
#
# 1 <= m <= 10^3
#
# 0 <= k <= 10^3
#

# @lc code=start
class Solution:
    def minSensors(self, n: int, m: int, k: int) -> int:
        """
        Interview explanation:
        Chebyshev radius k covers a (2k+1)×(2k+1) square — tile the grid
        with those blocks.

        Algorithm:
        - side = 2*k+1; return ceil(n/side) * ceil(m/side).

        Complexity: O(1).
        """
        side = 2 * k + 1
        return ((n + side - 1) // side) * ((m + side - 1) // side)
# @lc code=end

