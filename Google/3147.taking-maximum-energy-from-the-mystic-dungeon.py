#
# @lc app=leetcode id=3147 lang=python3
#
# [3147] Taking Maximum Energy From the Mystic Dungeon
#
# https://leetcode.com/problems/taking-maximum-energy-from-the-mystic-dungeon/description/
#
# algorithms
# Medium (60.88%)
# Likes:    594
# Dislikes: 40
# Total Accepted:    143.9K
# Total Submissions: 236.4K
# Testcase Example:  "[5,2,-10,-5,1]\n3"
#
#
# In a mystic dungeon, n magicians are standing in a line. Each magician
# has an attribute that gives you energy. Some magicians can give you
# negative energy, which means taking energy from you.
#
# You have been cursed in such a way that after absorbing energy from
# magician i, you will be instantly transported to magician (i + k). This
# process will be repeated until you reach the magician where (i + k) does
# not exist.
#
# In other words, you will choose a starting point and then teleport with
# k jumps until you reach the end of the magicians' sequence, absorbing
# all the energy during the journey.
#
# You are given an array energy and an integer k. Return the maximum
# possible energy you can gain.
#
# Note that when you reach a magician, you must take energy from them,
# whether it is negative or positive energy.
#
# Example 1:
#
# Input:  energy = [5,2,-10,-5,1], k = 3
#
# Output: 3
#
# Explanation: We can gain a total energy of 3 by starting from magician 1
# absorbing 2 + 1 = 3.
#
# Example 2:
#
# Input: energy = [-2,-3,-1], k = 2
#
# Output: -1
#
# Explanation: We can gain a total energy of -1 by starting from magician
# 2.
#
# Constraints:
#
# 1 <= energy.length <= 10^5
#
# -1000 <= energy[i] <= 1000
#
# 1 <= k <= energy.length - 1
#
# ​​​​​​
#

# @lc code=start
from typing import List


class Solution:
    def maximumEnergy(self, energy: List[int], k: int) -> int:
        """
        Interview explanation:
        Starting at i, you must take energy[i], energy[i+k], energy[i+2k], ...
        Choose the start that maximizes the sum.

        Algorithm:
        - Backward DP: dp[i] = energy[i] + (dp[i+k] if in range else 0).
        - Answer is max(dp).

        Complexity: O(n) time, O(1) extra space (in-place on a copy / array).
        """
        n = len(energy)
        dp = energy[:]
        for i in range(n - 1, -1, -1):
            if i + k < n:
                dp[i] += dp[i + k]
        return max(dp)

    def maximumEnergy_by_residue(self, energy: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: each residue class mod k is an independent suffix-max chain.

        Algorithm:
        - For each r in 0..k-1, walk indices n-1-r, n-1-r-k, ... accumulating
          suffix sums; track the global max.

        Complexity: O(n) time, O(1) space.
        """
        n = len(energy)
        ans = energy[-1]
        for r in range(k):
            total = 0
            i = n - 1 - r
            while i >= 0:
                total += energy[i]
                ans = max(ans, total)
                i -= k
        return ans
# @lc code=end
