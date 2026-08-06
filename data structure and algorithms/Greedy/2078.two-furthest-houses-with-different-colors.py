#
# @lc app=leetcode id=2078 lang=python3
#
# [2078] Two Furthest Houses With Different Colors
#
# https://leetcode.com/problems/two-furthest-houses-with-different-colors/description/
#
# algorithms
# Easy (71.71%)
# Likes:    1333
# Dislikes: 44
# Total Accepted:    224.9K
# Total Submissions: 313.7K
# Testcase Example:  "[1,1,1,6,1,1,1]"
#
# There are n houses evenly lined up on the street, and each house is
# beautifully painted. You are given a 0-indexed integer array colors of length
# n, where colors[i] represents the color of the i^th house.
#
# Return the maximum distance between two houses with different colors.
#
# The distance between the i^th and j^th houses is abs(i - j), where abs(x) is
# the absolute value of x.
#
#
#
# Example 1:
#
# Input: colors = [1,1,1,6,1,1,1]
# Output: 3
# Explanation: In the above image, color 1 is blue, and color 6 is red.
# The furthest two houses with different colors are house 0 and house 3.
# House 0 has color 1, and house 3 has color 6. The distance between them is
# abs(0 - 3) = 3.
# Note that houses 3 and 6 can also produce the optimal answer.
#
# Example 2:
#
# Input: colors = [1,8,3,8,3]
# Output: 4
# Explanation: In the above image, color 1 is blue, color 8 is yellow, and color
# 3 is green.
# The furthest two houses with different colors are house 0 and house 4.
# House 0 has color 1, and house 4 has color 3. The distance between them is
# abs(0 - 4) = 4.
#
# Example 3:
#
# Input: colors = [0,1]
# Output: 1
# Explanation: The furthest two houses with different colors are house 0 and
# house 1.
# House 0 has color 0, and house 1 has color 1. The distance between them is
# abs(0 - 1) = 1.
#
#
#
# Constraints:
#
#
# n == colors.length
#
#
# 2 <= n <= 100
#
#
# 0 <= colors[i] <= 100
#
#
# Test data are generated such that at least two houses have different colors.
#

# @lc code=start
from typing import List


class Solution:
    def maxDistance(self, colors: List[int]) -> int:
        """
        Interview explanation:
        Max |i-j| among houses with different colors. The answer always involves
        an endpoint of the array.

        Algorithm:
        - From left end, find rightmost different color; from right end, leftmost
          different; take max distance.

        Complexity: O(n) time, O(1) space.
        """
        n = len(colors)
        ans = 0
        for i in range(n):
            if colors[i] != colors[0]:
                ans = max(ans, i)
            if colors[i] != colors[n - 1]:
                ans = max(ans, n - 1 - i)
        return ans
# @lc code=end
