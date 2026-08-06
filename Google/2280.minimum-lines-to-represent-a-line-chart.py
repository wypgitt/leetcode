#
# @lc app=leetcode id=2280 lang=python3
#
# [2280] Minimum Lines to Represent a Line Chart
#
# https://leetcode.com/problems/minimum-lines-to-represent-a-line-chart/description/
#
# algorithms
# Medium (27.29%)
# Likes:    367
# Dislikes: 534
# Total Accepted:    33.3K
# Total Submissions: 121.9K
# Testcase Example:  "[[1,7],[2,6],[3,5],[4,4],[5,4],[6,3],[7,2],[8,1]]"
#
# You are given a 2D integer array stockPrices where stockPrices[i] = [day_i,
# price_i] indicates the price of the stock on day day_i is price_i. A line
# chart is created from the array by plotting the points on an XY plane with the
# X-axis representing the day and the Y-axis representing the price and
# connecting adjacent points. One such example is shown below:
#
# Return the minimum number of lines needed to represent the line chart.
#
#
#
# Example 1:
#
# Input: stockPrices = [[1,7],[2,6],[3,5],[4,4],[5,4],[6,3],[7,2],[8,1]]
# Output: 3
# Explanation:
# The diagram above represents the input, with the X-axis representing the day
# and Y-axis representing the price.
# The following 3 lines can be drawn to represent the line chart:
# - Line 1 (in red) from (1,7) to (4,4) passing through (1,7), (2,6), (3,5), and
# (4,4).
# - Line 2 (in blue) from (4,4) to (5,4).
# - Line 3 (in green) from (5,4) to (8,1) passing through (5,4), (6,3), (7,2),
# and (8,1).
# It can be shown that it is not possible to represent the line chart using less
# than 3 lines.
#
# Example 2:
#
# Input: stockPrices = [[3,4],[1,2],[7,8],[2,3]]
# Output: 1
# Explanation:
# As shown in the diagram above, the line chart can be represented with a single
# line.
#
#
#
# Constraints:
#
#
# 1 <= stockPrices.length <= 10^5
#
#
# stockPrices[i].length == 2
#
#
# 1 <= day_i, price_i <= 10^9
#
#
# All day_i are distinct.
#

# @lc code=start
from typing import List


class Solution:
    def minimumLines(self, stockPrices: List[List[int]]) -> int:
        """
        Interview explanation:
        Points (day, price); min straight segments covering points in day order
        (collinear consecutive points share a line).

        Algorithm:
        - Sort by day; count slope changes using cross-multiply equality.

        Complexity: O(n log n) time, O(1) extra space.
        """
        stockPrices.sort()
        n = len(stockPrices)
        if n <= 1:
            return 0
        ans = 1
        for i in range(2, n):
            x0, y0 = stockPrices[i - 2]
            x1, y1 = stockPrices[i - 1]
            x2, y2 = stockPrices[i]
            if (y1 - y0) * (x2 - x1) != (y2 - y1) * (x1 - x0):
                ans += 1
        return ans

# @lc code=end
