#
# @lc app=leetcode id=1954 lang=python3
#
# [1954] Minimum Garden Perimeter to Collect Enough Apples
#
# https://leetcode.com/problems/minimum-garden-perimeter-to-collect-enough-apples/description/
#
# algorithms
# Medium (55.63%)
# Likes:    410
# Dislikes: 99
# Total Accepted:    22.2K
# Total Submissions: 39.9K
# Testcase Example:  "1"
#
# In a garden represented as an infinite 2D grid, there is an apple tree
# planted at every integer coordinate. The apple tree planted at an integer
# coordinate (i, j) has |i| + |j| apples growing on it.
#
# You will buy an axis-aligned square plot of land that is centered at (0, 0).
#
# Given an integer neededApples, return the minimum perimeter of a plot such
# that at least neededApples apples are inside or on the perimeter of that
# plot.
#
# The value of |x| is defined as:
#
# x if x >= 0
#
# -x if x < 0
#
# Example 1:
#
# Input: neededApples = 1
# Output: 8
# Explanation: A square plot of side length 1 does not contain any apples.
# However, a square plot of side length 2 has 12 apples inside (as depicted in
# the image above).
# The perimeter is 2 * 4 = 8.
#
# Example 2:
#
# Input: neededApples = 13
# Output: 16
#
# Example 3:
#
# Input: neededApples = 1000000000
# Output: 5040
#
# Constraints:
#
# 1 <= neededApples <= 10^15
#

# @lc code=start
class Solution:
    def minimumPerimeter(self, neededApples: int) -> int:
        """
        Interview explanation:
        Lattice apples at (x,y) equal |x|+|y|. Centered square radius k
        (perimeter 8k) holds 2*k*(k+1)*(2k+1) apples. Minimal such k.

        Algorithm:
        - Search k; apples(k)=2*k*(k+1)*(2k+1); return 8*k.

        Complexity: O(log neededApples) time, O(1) space.
        """
        lo, hi = 1, 10**6
        while lo < hi:
            mid = (lo + hi) // 2
            apples = 2 * mid * (mid + 1) * (2 * mid + 1)
            if apples >= neededApples:
                hi = mid
            else:
                lo = mid + 1
        return 8 * lo

    def minimumPerimeter_linear(self, neededApples: int) -> int:
        """
        Interview explanation:
        Alternate: grow k until the apple formula meets the need.

        Algorithm:
        - Increment k until 2*k*(k+1)*(2k+1) >= neededApples.

        Complexity: O(k) ~ O(needed^(1/3)) time, O(1) space.
        """
        k = 1
        while 2 * k * (k + 1) * (2 * k + 1) < neededApples:
            k += 1
        return 8 * k
# @lc code=end

