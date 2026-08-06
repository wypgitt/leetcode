#
# @lc app=leetcode id=1691 lang=python3
#
# [1691] Maximum Height by Stacking Cuboids 
#
# https://leetcode.com/problems/maximum-height-by-stacking-cuboids/description/
#
# algorithms
# Hard (62.41%)
# Likes:    1277
# Dislikes: 36
# Total Accepted:    47.7K
# Total Submissions: 76.4K
# Testcase Example:  "[[50,45,20],[95,37,53],[45,23,12]]"
#
# Given n cuboids where the dimensions of the i^th cuboid is cuboids[i] =
# [width_i, length_i, height_i] (0-indexed). Choose a subset of cuboids and
# place them on each other.
#
# You can place cuboid i on cuboid j if width_i <= width_j and length_i <=
# length_j and height_i <= height_j. You can rearrange any cuboid's dimensions
# by rotating it to put it on another cuboid.
#
# Return the maximum height of the stacked cuboids.
#
# Example 1:
#
# Input: cuboids = [[50,45,20],[95,37,53],[45,23,12]]
# Output: 190
# Explanation:
# Cuboid 1 is placed on the bottom with the 53x37 side facing down with height
# 95.
# Cuboid 0 is placed next with the 45x20 side facing down with height 50.
# Cuboid 2 is placed next with the 23x12 side facing down with height 45.
# The total height is 95 + 50 + 45 = 190.
#
# Example 2:
#
# Input: cuboids = [[38,25,45],[76,35,3]]
# Output: 76
# Explanation:
# You can't place any of the cuboids on the other.
# We choose cuboid 1 and rotate it so that the 35x3 side is facing down and its
# height is 76.
#
# Example 3:
#
# Input: cuboids =
# [[7,11,17],[7,17,11],[11,7,17],[11,17,7],[17,7,11],[17,11,7]]
# Output: 102
# Explanation:
# After rearranging the cuboids, you can see that all cuboids have the same
# dimension.
# You can place the 11x7 side down on all cuboids so their heights are 17.
# The maximum height of stacked cuboids is 6 * 17 = 102.
#
# Constraints:
#
# n == cuboids.length
#
# 1 <= n <= 100
#
# 1 <= width_i, length_i, height_i <= 100
#

# @lc code=start
from typing import List


class Solution:
    def maxHeight(self, cuboids: List[List[int]]) -> int:
        """
        Interview explanation:
        Stack cuboids if w1<=w2,l1<=l2,h1<=h2 (any dimension permutation).
        Sort each cuboid's dims; sort cuboids; LIS-style DP on height.

        Algorithm:
        - For each cuboid sort 3 dims; sort list; dp[i]=h[i]+max(dp[j] if cuboids[j]<=cuboids[i])

        Complexity: O(n^2) time, O(n) space.
        """
        cubes = [sorted(c) for c in cuboids]
        cubes.sort()
        n = len(cubes)
        dp = [0] * n
        ans = 0
        for i in range(n):
            dp[i] = cubes[i][2]
            for j in range(i):
                if (
                    cubes[j][0] <= cubes[i][0]
                    and cubes[j][1] <= cubes[i][1]
                    and cubes[j][2] <= cubes[i][2]
                ):
                    dp[i] = max(dp[i], dp[j] + cubes[i][2])
            ans = max(ans, dp[i])
        return ans
# @lc code=end
