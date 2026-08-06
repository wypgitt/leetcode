#
# @lc app=leetcode id=3075 lang=python3
#
# [3075] Maximize Happiness of Selected Children
#
# https://leetcode.com/problems/maximize-happiness-of-selected-children/description/
#
# algorithms
# Medium (58.72%)
# Likes:    951
# Dislikes: 100
# Total Accepted:    290.7K
# Total Submissions: 495.1K
# Testcase Example:  "[1,2,3]\n2"
#
#
# You are given an array happiness of length n, and a positive integer k.
#
# There are n children standing in a queue, where the i^th child has
# happiness value happiness[i]. You want to select k children from these n
# children in k turns.
#
# In each turn, when you select a child, the happiness value of all the
# children that have not been selected till now decreases by 1. Note that
# the happiness value cannot become negative and gets decremented only if
# it is positive.
#
# Return the maximum sum of the happiness values of the selected children
# you can achieve by selecting k children.
#
# Example 1:
#
# Input: happiness = [1,2,3], k = 2
# Output: 4
# Explanation: We can pick 2 children in the following way:
# - Pick the child with the happiness value == 3. The happiness value of
# the remaining children becomes [0,1].
# - Pick the child with the happiness value == 1. The happiness value of
# the remaining child becomes [0]. Note that the happiness value cannot
# become less than 0.
# The sum of the happiness values of the selected children is 3 + 1 = 4.
#
# Example 2:
#
# Input: happiness = [1,1,1,1], k = 2
# Output: 1
# Explanation: We can pick 2 children in the following way:
# - Pick any child with the happiness value == 1. The happiness value of
# the remaining children becomes [0,0,0].
# - Pick the child with the happiness value == 0. The happiness value of
# the remaining child becomes [0,0].
# The sum of the happiness values of the selected children is 1 + 0 = 1.
#
# Example 3:
#
# Input: happiness = [2,3,4,5], k = 1
# Output: 5
# Explanation: We can pick 1 child in the following way:
# - Pick the child with the happiness value == 5. The happiness value of
# the remaining children becomes [1,2,3].
# The sum of the happiness values of the selected children is 5.
#
# Constraints:
#
# 1 <= n == happiness.length <= 2 * 10^5
#
# 1 <= happiness[i] <= 10^8
#
# 1 <= k <= n
#

# @lc code=start
from typing import List


class Solution:
    def maximumHappinessSum(self, happiness: List[int], k: int) -> int:
        """
        Interview explanation:
        Each selection decrements all remaining happiness by 1 (floored at 0).
        Greedy: always pick the current largest; the t-th pick (0-indexed) of a
        sorted-desc array contributes max(h[t] - t, 0).

        Algorithm:
        - Sort descending; sum max(happiness[i] - i, 0) for i in 0..k-1.

        Complexity: O(n log n) time, O(n) space.
        """
        happiness.sort(reverse=True)
        total = 0
        for i in range(k):
            val = happiness[i] - i
            if val <= 0:
                break
            total += val
        return total

    def maximumHappinessSum_nlargest(self, happiness: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: heapq.nlargest to avoid full sort when k << n.

        Algorithm:
        - Take k largest, sort them desc, same contribution formula.

        Complexity: O(n log k + k log k) time, O(k) space.
        """
        import heapq

        top = heapq.nlargest(k, happiness)
        top.sort(reverse=True)
        return sum(max(top[i] - i, 0) for i in range(k))
# @lc code=end
