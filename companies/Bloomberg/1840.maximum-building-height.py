#
# @lc app=leetcode id=1840 lang=python3
#
# [1840] Maximum Building Height
#
# https://leetcode.com/problems/maximum-building-height/description/
#
# algorithms
# Hard (66.99%)
# Likes:    749
# Dislikes: 38
# Total Accepted:    84.1K
# Total Submissions: 126K
# Testcase Example:  "5"
#
# You want to build n new buildings in a city. The new buildings will be built
# in a line and are labeled from 1 to n.
#
# However, there are city restrictions on the heights of the new buildings:
#
# The height of each building must be a non-negative integer.
#
# The height of the first building must be 0.
#
# The height difference between any two adjacent buildings cannot exceed 1.
#
# Additionally, there are city restrictions on the maximum height of specific
# buildings. These restrictions are given as a 2D integer array restrictions
# where restrictions[i] = [id_i, maxHeight_i] indicates that building id_i must
# have a height less than or equal to maxHeight_i.
#
# It is guaranteed that each building will appear at most once in restrictions,
# and building 1 will not be in restrictions.
#
# Return the maximum possible height of the tallest building.
#
# Example 1:
#
# Input: n = 5, restrictions = [[2,1],[4,1]]
# Output: 2
# Explanation: The green area in the image indicates the maximum allowed height
# for each building.
# We can build the buildings with heights [0,1,2,1,2], and the tallest building
# has a height of 2.
#
# Example 2:
#
# Input: n = 6, restrictions = []
# Output: 5
# Explanation: The green area in the image indicates the maximum allowed height
# for each building.
# We can build the buildings with heights [0,1,2,3,4,5], and the tallest
# building has a height of 5.
#
# Example 3:
#
# Input: n = 10, restrictions = [[5,3],[2,5],[7,4],[10,3]]
# Output: 5
# Explanation: The green area in the image indicates the maximum allowed height
# for each building.
# We can build the buildings with heights [0,1,2,3,3,4,4,5,4,3], and the
# tallest building has a height of 5.
#
# Constraints:
#
# 2 <= n <= 10^9
#
# 0 <= restrictions.length <= min(n - 1, 10^5)
#
# 2 <= id_i <= n
#
# id_i is unique.
#
# 0 <= maxHeight_i <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def maxBuilding(self, n: int, restrictions: List[List[int]]) -> int:
        """
        Interview explanation:
        Building heights: h[1]=0; |h[i]-h[i+1]|<=1; respect restrictions.
        Max reachable height anywhere. Propagate constraints L->R and R->L,
        then max peak between consecutive restriction points.

        Algorithm (sort + two-pass tighten + peaks):
        - Add (1,0) and (n,n-1); sort by id; forward/backward min with distance;
          between i,i+1 max height = (h_i+h_j+dist)//2.

        Complexity: O(r log r) time, O(r) space.
        """
        rest = restrictions + [[1, 0], [n, n - 1]]
        rest.sort()
        m = len(rest)
        for i in range(1, m):
            d = rest[i][0] - rest[i - 1][0]
            rest[i][1] = min(rest[i][1], rest[i - 1][1] + d)
        for i in range(m - 2, -1, -1):
            d = rest[i + 1][0] - rest[i][0]
            rest[i][1] = min(rest[i][1], rest[i + 1][1] + d)
        ans = 0
        for i in range(1, m):
            left, hl = rest[i - 1]
            right, hr = rest[i]
            ans = max(ans, (hl + hr + right - left) // 2)
        return ans
# @lc code=end
