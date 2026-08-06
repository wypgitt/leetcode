#
# @lc app=leetcode id=1732 lang=python3
#
# [1732] Find the Highest Altitude
#
# https://leetcode.com/problems/find-the-highest-altitude/description/
#
# algorithms
# Easy (84.64%)
# Likes:    3506
# Dislikes: 447
# Total Accepted:    911K
# Total Submissions: 1.1M
# Testcase Example:  "[-5,1,5,0,-7]"
#
# There is a biker going on a road trip. The road trip consists of n + 1 points
# at various altitudes. The biker starts his trip on point 0 with altitude
# equal 0.
#
# You are given an integer array gain of length n where gain[i] is the net gain
# in altitude between points i and i + 1 for all (0 <= i < n). Return the
# highest altitude of a point.
#
# Example 1:
#
# Input: gain = [-5,1,5,0,-7]
# Output: 1
# Explanation: The altitudes are [0,-5,-4,1,1,-6]. The highest is 1.
#
# Example 2:
#
# Input: gain = [-4,-3,-2,-1,4,3,2]
# Output: 0
# Explanation: The altitudes are [0,-4,-7,-9,-10,-6,-3,-1]. The highest is 0.
#
# Constraints:
#
# n == gain.length
#
# 1 <= n <= 100
#
# -100 <= gain[i] <= 100
#

# @lc code=start
from typing import List


class Solution:
    def largestAltitude(self, gain: List[int]) -> int:
        """
        Interview explanation:
        Altitude starts at 0; gain[i] is net change. Track running sum and max.

        Algorithm:
        - h = ans = 0; for g in gain: h += g; ans = max(ans, h)

        Complexity: O(n) time, O(1) space.
        """
        h = ans = 0
        for g in gain:
            h += g
            if h > ans:
                ans = h
        return ans

    def largestAltitude_prefix(self, gain: List[int]) -> int:
        """
        Interview explanation:
        Alternate: build full prefix altitudes and take max (includes 0).

        Algorithm:
        - prefixes; return max

        Complexity: O(n) time, O(n) space.
        """
        alt = [0]
        for g in gain:
            alt.append(alt[-1] + g)
        return max(alt)
# @lc code=end
