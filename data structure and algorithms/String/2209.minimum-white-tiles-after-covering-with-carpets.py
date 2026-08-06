#
# @lc app=leetcode id=2209 lang=python3
#
# [2209] Minimum White Tiles After Covering With Carpets
#
# https://leetcode.com/problems/minimum-white-tiles-after-covering-with-carpets/description/
#
# algorithms
# Hard (39.17%)
# Likes:    525
# Dislikes: 17
# Total Accepted:    16.8K
# Total Submissions: 42.9K
# Testcase Example:  "\"10110101\"\n2\n2"
#
# You are given a 0-indexed binary string floor, which represents the colors of
# tiles on a floor:
#
#
# floor[i] = '0' denotes that the i^th tile of the floor is colored black.
#
#
# On the other hand, floor[i] = '1' denotes that the i^th tile of the floor is
# colored white.
#
# You are also given numCarpets and carpetLen. You have numCarpets black
# carpets, each of length carpetLen tiles. Cover the tiles with the given
# carpets such that the number of white tiles still visible is minimum. Carpets
# may overlap one another.
#
# Return the minimum number of white tiles still visible.
#
#
#
# Example 1:
#
# Input: floor = "10110101", numCarpets = 2, carpetLen = 2
# Output: 2
# Explanation:
# The figure above shows one way of covering the tiles with the carpets such
# that only 2 white tiles are visible.
# No other way of covering the tiles with the carpets can leave less than 2
# white tiles visible.
#
# Example 2:
#
# Input: floor = "11111", numCarpets = 2, carpetLen = 3
# Output: 0
# Explanation:
# The figure above shows one way of covering the tiles with the carpets such
# that no white tiles are visible.
# Note that the carpets are able to overlap one another.
#
#
#
# Constraints:
#
#
# 1 <= carpetLen <= floor.length <= 1000
#
#
# floor[i] is either '0' or '1'.
#
#
# 1 <= numCarpets <= 1000
#

# @lc code=start
class Solution:
    def minimumWhiteTiles(self, floor: str, numCarpets: int, carpetLen: int) -> int:
        """
        Interview explanation:
        Cover floor (0 black / 1 white) with up to numCarpets carpets of length
        carpetLen; minimize remaining white tiles.

        Algorithm:
        (DP)
        - dp[i][j]: min whites in suffix floor[i:] with j carpets.
        - At i: leave tile (pay if white) or place carpet covering [i,i+len).

        Complexity: O(n * numCarpets) time and space.
        """
        n = len(floor)
        dp = [[0] * (numCarpets + 1) for _ in range(n + 1)]
        for i in range(n - 1, -1, -1):
            for j in range(numCarpets + 1):
                leave = dp[i + 1][j] + (floor[i] == "1")
                cover = leave
                if j > 0:
                    cover = dp[min(n, i + carpetLen)][j - 1]
                dp[i][j] = min(leave, cover)
        return dp[0][numCarpets]
# @lc code=end
