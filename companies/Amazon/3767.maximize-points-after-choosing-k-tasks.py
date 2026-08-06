#
# @lc app=leetcode id=3767 lang=python3
#
# [3767] Maximize Points After Choosing K Tasks
#
# https://leetcode.com/problems/maximize-points-after-choosing-k-tasks/description/
#
# algorithms
# Medium (59.14%)
# Likes:    83
# Dislikes: 6
# Total Accepted:    17.6K
# Total Submissions: 29.7K
# Testcase Example:  "[5,2,10]\n[10,3,8]\n2"
#
#
# You are given two integer arrays, technique1 and technique2, each of
# length n, where n represents the number of tasks to complete.
#
# If the i^th task is completed using technique 1, you earn technique1[i]
# points.
#
# If it is completed using technique 2, you earn technique2[i] points.
#
# You are also given an integer k, representing the minimum number of
# tasks that must be completed using technique 1.
#
# You must complete at least k tasks using technique 1 (they do not need
# to be the first k tasks).
#
# The remaining tasks may be completed using either technique.
#
# Return an integer denoting the maximum total points you can earn.
#
# Example 1:
#
# Input: technique1 = [5,2,10], technique2 = [10,3,8], k = 2
#
# Output: 22
#
# Explanation:
#
# We must complete at least k = 2 tasks using technique1.
#
# Choosing technique1[1] and technique1[2] (completed using technique 1),
# and technique2[0] (completed using technique 2), yields the maximum
# points: 2 + 10 + 10 = 22.
#
# Example 2:
#
# Input: technique1 = [10,20,30], technique2 = [5,15,25], k = 2
#
# Output: 60
#
# Explanation:
#
# We must complete at least k = 2 tasks using technique1.
#
# Choosing all tasks using technique 1 yields the maximum points: 10 + 20
# + 30 = 60.
#
# Example 3:
#
# Input: technique1 = [1,2,3], technique2 = [4,5,6], k = 0
#
# Output: 15
#
# Explanation:
#
# Since k = 0, we are not required to choose any task using technique1.
#
# Choosing all tasks using technique 2 yields the maximum points: 4 + 5 +
# 6 = 15.
#
# Constraints:
#
# 1 <= n == technique1.length == technique2.length <= 10^5
#
# 1 <= technique1[i], technique2​​​​​​​[i] <= 10^​​​​​​​5
#
# 0 <= k <= n
#

# @lc code=start
from typing import List


class Solution:
    def maxPoints(self, technique1: List[int], technique2: List[int], k: int) -> int:
        """
        Interview explanation:
        Must use technique1 on at least k tasks. Prefer technique1 where its
        advantage (t1 - t2) is largest; elsewhere take max(t1, t2).

        Algorithm:
        - Sort indices by (technique1 - technique2) descending.
        - Force first k to technique1; for the rest take max of the two.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(technique1)
        order = sorted(range(n), key=lambda i: technique1[i] - technique2[i], reverse=True)
        total = 0
        for j, i in enumerate(order):
            if j < k:
                total += technique1[i]
            else:
                total += max(technique1[i], technique2[i])
        return total

    def maxPoints_gain(self, technique1: List[int], technique2: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: start from all technique2, then apply the k largest positive
        switches plus any extra positive gains.

        Algorithm:
        - base = sum(technique2); gains = t1-t2 sorted desc; add top gains with >=k forced.

        Complexity: O(n log n) time, O(n) space.
        """
        gains = sorted((a - b for a, b in zip(technique1, technique2)), reverse=True)
        return sum(technique2) + sum(gains[:k]) + sum(g for g in gains[k:] if g > 0)
# @lc code=end
