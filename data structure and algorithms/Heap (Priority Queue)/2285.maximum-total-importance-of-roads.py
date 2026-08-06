#
# @lc app=leetcode id=2285 lang=python3
#
# [2285] Maximum Total Importance of Roads
#
# https://leetcode.com/problems/maximum-total-importance-of-roads/description/
#
# algorithms
# Medium (69.09%)
# Likes:    1372
# Dislikes: 84
# Total Accepted:    165.3K
# Total Submissions: 239.3K
# Testcase Example:  "5\n[[0,1],[1,2],[2,3],[0,2],[1,3],[2,4]]"
#
# You are given an integer n denoting the number of cities in a country. The
# cities are numbered from 0 to n - 1.
#
# You are also given a 2D integer array roads where roads[i] = [a_i, b_i]
# denotes that there exists a bidirectional road connecting cities a_i and b_i.
#
# You need to assign each city with an integer value from 1 to n, where each
# value can only be used once. The importance of a road is then defined as the
# sum of the values of the two cities it connects.
#
# Return the maximum total importance of all roads possible after assigning the
# values optimally.
#
#
#
# Example 1:
#
# Input: n = 5, roads = [[0,1],[1,2],[2,3],[0,2],[1,3],[2,4]]
# Output: 43
# Explanation: The figure above shows the country and the assigned values of
# [2,4,5,3,1].
# - The road (0,1) has an importance of 2 + 4 = 6.
# - The road (1,2) has an importance of 4 + 5 = 9.
# - The road (2,3) has an importance of 5 + 3 = 8.
# - The road (0,2) has an importance of 2 + 5 = 7.
# - The road (1,3) has an importance of 4 + 3 = 7.
# - The road (2,4) has an importance of 5 + 1 = 6.
# The total importance of all roads is 6 + 9 + 8 + 7 + 7 + 6 = 43.
# It can be shown that we cannot obtain a greater total importance than 43.
#
# Example 2:
#
# Input: n = 5, roads = [[0,3],[2,4],[1,3]]
# Output: 20
# Explanation: The figure above shows the country and the assigned values of
# [4,3,2,5,1].
# - The road (0,3) has an importance of 4 + 5 = 9.
# - The road (2,4) has an importance of 2 + 1 = 3.
# - The road (1,3) has an importance of 3 + 5 = 8.
# The total importance of all roads is 9 + 3 + 8 = 20.
# It can be shown that we cannot obtain a greater total importance than 20.
#
#
#
# Constraints:
#
#
# 2 <= n <= 5 * 10^4
#
#
# 1 <= roads.length <= 5 * 10^4
#
#
# roads[i].length == 2
#
#
# 0 <= a_i, b_i <= n - 1
#
#
# a_i != b_i
#
#
# There are no duplicate roads.
#

# @lc code=start
from typing import List


class Solution:
    def maximumImportance(self, n: int, roads: List[List[int]]) -> int:
        """
        Interview explanation:
        Assign distinct values 1..n to cities; road importance = sum of endpoints.
        Maximize total importance.

        Algorithm:
        - Degree greedy: higher degree gets higher value; sort degrees, zip 1..n.

        Complexity: O(n log n + m) time, O(n) space.
        """
        deg = [0] * n
        for a, b in roads:
            deg[a] += 1
            deg[b] += 1
        deg.sort()
        return sum(d * v for d, v in zip(deg, range(1, n + 1)))
# @lc code=end
