#
# @lc app=leetcode id=3492 lang=python3
#
# [3492] Maximum Containers on a Ship
#
# https://leetcode.com/problems/maximum-containers-on-a-ship/description/
#
# algorithms
# Easy (75.55%)
# Likes:    69
# Dislikes: 13
# Total Accepted:    53.3K
# Total Submissions: 70.6K
# Testcase Example:  "2\n3\n15"
#
#
# You are given a positive integer n representing an n x n cargo deck on a
# ship. Each cell on the deck can hold one container with a weight of
# exactly w.
#
# However, the total weight of all containers, if loaded onto the deck,
# must not exceed the ship's maximum weight capacity, maxWeight.
#
# Return the maximum number of containers that can be loaded onto the
# ship.
#
# Example 1:
#
# Input: n = 2, w = 3, maxWeight = 15
#
# Output: 4
#
# Explanation:
#
# The deck has 4 cells, and each container weighs 3. The total weight of
# loading all containers is 12, which does not exceed maxWeight.
#
# Example 2:
#
# Input: n = 3, w = 5, maxWeight = 20
#
# Output: 4
#
# Explanation:
#
# The deck has 9 cells, and each container weighs 5. The maximum number of
# containers that can be loaded without exceeding maxWeight is 4.
#
# Constraints:
#
# 1 <= n <= 1000
#
# 1 <= w <= 1000
#
# 1 <= maxWeight <= 10^9
#

# @lc code=start
class Solution:
    def maxContainers(self, n: int, w: int, maxWeight: int) -> int:
        """
        Interview explanation:
        Deck has n^2 cells; each container weighs w; total weight ≤ maxWeight.

        Algorithm:
        - Answer is min(n*n, maxWeight // w).

        Complexity: O(1) time/space.
        """
        return min(n * n, maxWeight // w)
# @lc code=end
