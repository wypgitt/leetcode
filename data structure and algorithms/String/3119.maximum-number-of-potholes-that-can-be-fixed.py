#
# @lc app=leetcode id=3119 lang=python3
#
# [3119] Maximum Number of Potholes That Can Be Fixed
#
# https://leetcode.com/problems/maximum-number-of-potholes-that-can-be-fixed/description/
#
# algorithms
# Medium (53.46%)
# Likes:    21
# Dislikes: 3
# Total Accepted:    4.2K
# Total Submissions: 7.9K
# Testcase Example:  "\"..\"\n5"
#
#
# You are given a string road, consisting only of characters "x" and ".",
# where each "x" denotes a pothole and each "." denotes a smooth road, and
# an integer budget.
#
# In one repair operation, you can repair n consecutive potholes for a
# price of n + 1.
#
# Return the maximum number of potholes that can be fixed such that the
# sum of the prices of all of the fixes doesn't go over the given budget.
#
# Example 1:
#
# Input: road = "..", budget = 5
#
# Output: 0
#
# Explanation:
#
# There are no potholes to be fixed.
#
# Example 2:
#
# Input: road = "..xxxxx", budget = 4
#
# Output: 3
#
# Explanation:
#
# We fix the first three potholes (they are consecutive). The budget
# needed for this task is 3 + 1 = 4.
#
# Example 3:
#
# Input: road = "x.x.xxx...x", budget = 14
#
# Output: 6
#
# Explanation:
#
# We can fix all the potholes. The total cost would be (1 + 1) + (1 + 1) +
# (3 + 1) + (1 + 1) = 10 which is within our budget of 14.
#
# Constraints:
#
# 1 <= road.length <= 10^5
#
# 1 <= budget <= 10^5 + 1
#
# road consists only of characters '.' and 'x'.
#

# @lc code=start
class Solution:
    def maxPotholes(self, road: str, budget: int) -> int:
        """
        Interview explanation:
        Fix a contiguous run of n potholes for cost n+1. Maximize potholes fixed
        under budget.

        Algorithm:
        - Extract run lengths; greedily repair longest runs first (each run pays
          one fixed +1 overhead, so longer runs amortize better).
        - Partial repair of a run uses remaining budget-1 holes.

        Complexity: O(n + r log r) time, O(r) space.
        """
        ans = 0
        for length in sorted(map(len, road.split(".")), reverse=True):
            if length == 0:
                continue
            can_repair = max(0, budget - 1)
            if length > can_repair:
                return ans + can_repair
            ans += length
            budget -= length + 1
        return ans
# @lc code=end
