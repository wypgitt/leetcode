#
# @lc app=leetcode id=3207 lang=python3
#
# [3207] Maximum Points After Enemy Battles
#
# https://leetcode.com/problems/maximum-points-after-enemy-battles/description/
#
# algorithms
# Medium (33.38%)
# Likes:    132
# Dislikes: 43
# Total Accepted:    31.4K
# Total Submissions: 94K
# Testcase Example:  "[3,2,2]\n2"
#
#
# You are given an integer array enemyEnergies denoting the energy values
# of various enemies.
#
# You are also given an integer currentEnergy denoting the amount of
# energy you have initially.
#
# You start with 0 points, and all the enemies are unmarked initially.
#
# You can perform either of the following operations zero or multiple
# times to gain points:
#
# Choose an unmarked enemy, i, such that currentEnergy >=
# enemyEnergies[i]. By choosing this option:
#
# You gain 1 point.
#
# Your energy is reduced by the enemy's energy, i.e. currentEnergy =
# currentEnergy - enemyEnergies[i].
#
# If you have at least 1 point, you can choose an unmarked enemy, i. By
# choosing this option:
#
# Your energy increases by the enemy's energy, i.e. currentEnergy =
# currentEnergy + enemyEnergies[i].
#
# The enemy i is marked.
#
# Return an integer denoting the maximum points you can get in the end by
# optimally performing operations.
#
# Example 1:
#
# Input: enemyEnergies = [3,2,2], currentEnergy = 2
#
# Output: 3
#
# Explanation:
#
# The following operations can be performed to get 3 points, which is the
# maximum:
#
# First operation on enemy 1: points increases by 1, and currentEnergy
# decreases by 2. So, points = 1, and currentEnergy = 0.
#
# Second operation on enemy 0: currentEnergy increases by 3, and enemy 0
# is marked. So, points = 1, currentEnergy = 3, and marked enemies = [0].
#
# First operation on enemy 2: points increases by 1, and currentEnergy
# decreases by 2. So, points = 2, currentEnergy = 1, and marked enemies =
# [0].
#
# Second operation on enemy 2: currentEnergy increases by 2, and enemy 2
# is marked. So, points = 2, currentEnergy = 3, and marked enemies = [0,
# 2].
#
# First operation on enemy 1: points increases by 1, and currentEnergy
# decreases by 2. So, points = 3, currentEnergy = 1, and marked enemies =
# [0, 2].
#
# Example 2:
#
# Input: enemyEnergies = [2], currentEnergy = 10
#
# Output: 5
#
# Explanation:
#
# Performing the first operation 5 times on enemy 0 results in the maximum
# number of points.
#
# Constraints:
#
# 1 <= enemyEnergies.length <= 10^5
#
# 1 <= enemyEnergies[i] <= 10^9
#
# 0 <= currentEnergy <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def maximumPoints(self, enemyEnergies: List[int], currentEnergy: int) -> int:
        """
        Interview explanation:
        Point ops spend energy on an unmarked enemy (reusable); mark ops add that
        enemy's energy but require ≥1 point. Optimal: always spend against the
        cheapest enemy, and mark every other enemy for energy once.

        Algorithm:
        - Let m = min(enemyEnergies). If currentEnergy < m, return 0.
        - Total energy pool = currentEnergy + sum(energies) - m.
        - Points = pool // m.

        Complexity: O(n) time, O(1) space.
        """
        m = min(enemyEnergies)
        if currentEnergy < m:
            return 0
        return (currentEnergy + sum(enemyEnergies) - m) // m

    def maximumPoints_two_pointers(self, enemyEnergies: List[int], currentEnergy: int) -> int:
        """
        Interview explanation:
        Alternate: sort, two pointers — defeat cheapest for points, mark
        expensive for energy when needed.

        Algorithm:
        - Sort ascending. Left = cheap spend target; right = mark for energy.
        - While left <= right: if energy >= energies[left], take as many points
          as possible from it; else if points > 0, mark energies[right].

        Complexity: O(n log n) time, O(n) space for sort.
        """
        arr = sorted(enemyEnergies)
        left, right = 0, len(arr) - 1
        points = 0
        energy = currentEnergy
        while left <= right:
            if energy >= arr[left]:
                gain = energy // arr[left]
                points += gain
                energy -= gain * arr[left]
            elif points > 0:
                energy += arr[right]
                right -= 1
            else:
                break
        return points
# @lc code=end
