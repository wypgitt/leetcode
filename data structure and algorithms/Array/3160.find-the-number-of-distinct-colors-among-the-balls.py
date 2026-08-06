#
# @lc app=leetcode id=3160 lang=python3
#
# [3160] Find the Number of Distinct Colors Among the Balls
#
# https://leetcode.com/problems/find-the-number-of-distinct-colors-among-the-balls/description/
#
# algorithms
# Medium (54.07%)
# Likes:    772
# Dislikes: 95
# Total Accepted:    172.1K
# Total Submissions: 318.3K
# Testcase Example:  "4\n[[1,4],[2,5],[1,3],[3,4]]"
#
#
# You are given an integer limit and a 2D array queries of size n x 2.
#
# There are limit + 1 balls with distinct labels in the range [0, limit].
# Initially, all balls are uncolored. For every query in queries that is
# of the form [x, y], you mark ball x with the color y. After each query,
# you need to find the number of colors among the balls.
#
# Return an array result of length n, where result[i] denotes the number
# of colors after i^th query.
#
# Note that when answering a query, lack of a color will not be considered
# as a color.
#
# Example 1:
#
# Input: limit = 4, queries = [[1,4],[2,5],[1,3],[3,4]]
#
# Output: [1,2,2,3]
#
# Explanation:
#
# After query 0, ball 1 has color 4.
#
# After query 1, ball 1 has color 4, and ball 2 has color 5.
#
# After query 2, ball 1 has color 3, and ball 2 has color 5.
#
# After query 3, ball 1 has color 3, ball 2 has color 5, and ball 3 has
# color 4.
#
# Example 2:
#
# Input: limit = 4, queries = [[0,1],[1,2],[2,2],[3,4],[4,5]]
#
# Output: [1,2,2,3,4]
#
# Explanation:
#
# After query 0, ball 0 has color 1.
#
# After query 1, ball 0 has color 1, and ball 1 has color 2.
#
# After query 2, ball 0 has color 1, and balls 1 and 2 have color 2.
#
# After query 3, ball 0 has color 1, balls 1 and 2 have color 2, and ball
# 3 has color 4.
#
# After query 4, ball 0 has color 1, balls 1 and 2 have color 2, ball 3
# has color 4, and ball 4 has color 5.
#
# Constraints:
#
# 1 <= limit <= 10^9
#
# 1 <= n == queries.length <= 10^5
#
# queries[i].length == 2
#
# 0 <= queries[i][0] <= limit
#
# 1 <= queries[i][1] <= 10^9
#

# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def queryResults(self, limit: int, queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Balls start uncolored. Each query paints ball x with color y; after each
        query report how many distinct colors are in use (limit can be 1e9).

        Algorithm:
        - Map ball -> color and color -> count.
        - On repaint: decrement old color (drop if zero), set new, increment.
        - Append number of colors with positive count.

        Complexity: O(q) time, O(q) space (only touched balls).
        """
        ball_color: dict[int, int] = {}
        color_cnt: dict[int, int] = defaultdict(int)
        ans = []
        for x, y in queries:
            if x in ball_color:
                old = ball_color[x]
                color_cnt[old] -= 1
                if color_cnt[old] == 0:
                    del color_cnt[old]
            ball_color[x] = y
            color_cnt[y] += 1
            ans.append(len(color_cnt))
        return ans
# @lc code=end
