#
# @lc app=leetcode id=1395 lang=python3
#
# [1395] Count Number of Teams
#
# https://leetcode.com/problems/count-number-of-teams/description/
#
# algorithms
# Medium (70.16%)
# Likes:    3459
# Dislikes: 237
# Total Accepted:    244.7K
# Total Submissions: 348.8K
# Testcase Example:  '[2,5,3,4,1]'
#
# There are n soldiers standing in a line. Each soldier is assigned a unique
# rating value.
# 
# You have to form a team of 3 soldiers amongst them under the following
# rules:
# 
# 
# Choose 3 soldiers with index (i, j, k) with rating (rating[i], rating[j],
# rating[k]).
# A team is valid if: (rating[i] < rating[j] < rating[k]) or (rating[i] >
# rating[j] > rating[k]) where (0 <= i < j < k < n).
# 
# 
# Return the number of teams you can form given the conditions. (soldiers can
# be part of multiple teams).
# 
# 
# Example 1:
# 
# 
# Input: rating = [2,5,3,4,1]
# Output: 3
# Explanation: We can form three teams given the conditions. (2,3,4), (5,4,1),
# (5,3,1). 
# 
# 
# Example 2:
# 
# 
# Input: rating = [2,1,3]
# Output: 0
# Explanation: We can't form any team given the conditions.
# 
# 
# Example 3:
# 
# 
# Input: rating = [1,2,3,4]
# Output: 4
# 
# 
# 
# Constraints:
# 
# 
# n == rating.length
# 3 <= n <= 1000
# 1 <= rating[i] <= 10^5
# All the integers in rating are unique.
# 
# 
#

# @lc code=start
from __future__ import annotations

from typing import List


class Solution:
    def numTeams(self, rating: List[int]) -> int:
        teams = 0
        n = len(rating)

        for middle in range(n):
            smaller_left = greater_left = 0
            smaller_right = greater_right = 0

            for left in range(middle):
                if rating[left] < rating[middle]:
                    smaller_left += 1
                else:
                    greater_left += 1

            for right in range(middle + 1, n):
                if rating[right] > rating[middle]:
                    greater_right += 1
                else:
                    smaller_right += 1

            teams += smaller_left * greater_right
            teams += greater_left * smaller_right

        return teams
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# Treat each soldier as the middle member of the team. For increasing teams,
# choose a smaller rating on the left and a larger rating on the right. For
# decreasing teams, choose a larger rating on the left and a smaller rating on
# the right.
#
# Data structure:
# Four counters per middle index are enough; no extra arrays are necessary for
# the given constraints.
#
# Formula:
# For middle index `j`:
# - Increasing teams: `smaller_left * greater_right`.
# - Decreasing teams: `greater_left * smaller_right`.
#
# Edge cases:
# - Fewer than 3 soldiers: loops produce 0.
# - Strictly increasing array: only increasing teams count.
# - Strictly decreasing array: only decreasing teams count.
#
# Complexity:
# - Time: O(n^2), with n <= 200.
# - Space: O(1).
#
# Improvement:
# Fenwick trees can reduce this to O(n log n) for much larger n, but the
# O(n^2) middle-count method is simpler and ideal for the constraints.
