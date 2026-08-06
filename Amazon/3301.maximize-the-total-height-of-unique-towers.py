#
# @lc app=leetcode id=3301 lang=python3
#
# [3301] Maximize the Total Height of Unique Towers
#
# https://leetcode.com/problems/maximize-the-total-height-of-unique-towers/description/
#
# algorithms
# Medium (37.56%)
# Likes:    137
# Dislikes: 8
# Total Accepted:    35.8K
# Total Submissions: 95.2K
# Testcase Example:  "[2,3,4,3]"
#
#
# You are given an array maximumHeight, where maximumHeight[i] denotes the
# maximum height the i^th tower can be assigned.
#
# Your task is to assign a height to each tower so that:
#
# The height of the i^th tower is a positive integer and does not exceed
# maximumHeight[i].
#
# No two towers have the same height.
#
# Return the maximum possible total sum of the tower heights. If it's not
# possible to assign heights, return -1.
#
# Example 1:
#
# Input: maximumHeight = [2,3,4,3]
#
# Output: 10
#
# Explanation:
#
# We can assign heights in the following way: [1, 2, 4, 3].
#
# Example 2:
#
# Input: maximumHeight = [15,10]
#
# Output: 25
#
# Explanation:
#
# We can assign heights in the following way: [15, 10].
#
# Example 3:
#
# Input: maximumHeight = [2,2,1]
#
# Output: -1
#
# Explanation:
#
# It's impossible to assign positive heights to each index so that no two
# towers have the same height.
#
# Constraints:
#
# 1 <= maximumHeight.length <= 10^5
#
# 1 <= maximumHeight[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def maximumTotalSum(self, maximumHeight: List[int]) -> int:
        """
        Interview explanation:
        Assign distinct positive heights <= each tower's cap to maximize the sum.
        Prefer tallest feasible heights; greedily fill from the largest caps.

        Algorithm:
        - Sort caps descending.
        - Keep next = next unused height upper bound; assign min(cap, next).
        - If assignment <= 0, impossible (-1); else shrink next to assigned - 1.

        Complexity: O(n log n) time, O(n) space.
        """
        heights = sorted(maximumHeight, reverse=True)
        total = 0
        nxt = 10**18
        for h in heights:
            cur = min(h, nxt)
            if cur <= 0:
                return -1
            total += cur
            nxt = cur - 1
        return total

    def maximumTotalSum_set(self, maximumHeight: List[int]) -> int:
        """
        Interview explanation:
        Same greedy while tracking used heights explicitly.

        Algorithm:
        - Sort descending; for each cap take the largest unused h <= cap.

        Complexity: O(n log n + sum gaps) time, O(n) space.
        """
        used = set()
        total = 0
        for h in sorted(maximumHeight, reverse=True):
            while h > 0 and h in used:
                h -= 1
            if h <= 0:
                return -1
            used.add(h)
            total += h
        return total
# @lc code=end
