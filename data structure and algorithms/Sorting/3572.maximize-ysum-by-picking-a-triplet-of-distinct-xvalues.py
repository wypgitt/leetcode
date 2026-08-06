#
# @lc app=leetcode id=3572 lang=python3
#
# [3572] Maximize Y‑Sum by Picking a Triplet of Distinct X‑Values
#
# https://leetcode.com/problems/maximize-ysum-by-picking-a-triplet-of-distinct-xvalues/description/
#
# algorithms
# Medium (63.56%)
# Likes:    71
# Dislikes: 3
# Total Accepted:    32K
# Total Submissions: 50.4K
# Testcase Example:  "[1,2,1,3,2]\n[5,3,4,6,2]"
#
#
# You are given two integer arrays x and y, each of length n. You must
# choose three distinct indices i, j, and k such that:
#
# x[i] != x[j]
#
# x[j] != x[k]
#
# x[k] != x[i]
#
# Your goal is to maximize the value of y[i] + y[j] + y[k] under these
# conditions. Return the maximum possible sum that can be obtained by
# choosing such a triplet of indices.
#
# If no such triplet exists, return -1.
#
# Example 1:
#
# Input: x = [1,2,1,3,2], y = [5,3,4,6,2]
#
# Output: 14
#
# Explanation:
#
# Choose i = 0 (x[i] = 1, y[i] = 5), j = 1 (x[j] = 2, y[j] = 3), k = 3
# (x[k] = 3, y[k] = 6).
#
# All three values chosen from x are distinct. 5 + 3 + 6 = 14 is the
# maximum we can obtain. Hence, the output is 14.
#
# Example 2:
#
# Input: x = [1,2,1,2], y = [4,5,6,7]
#
# Output: -1
#
# Explanation:
#
# There are only two distinct values in x. Hence, the output is -1.
#
# Constraints:
#
# n == x.length == y.length
#
# 3 <= n <= 10^5
#
# 1 <= x[i], y[i] <= 10^6
#

# @lc code=start

from typing import List


class Solution:
    def maxSumDistinctTriplet(self, x: List[int], y: List[int]) -> int:
        """
        Interview explanation:
        For each distinct x-value keep only its maximum y; then the answer is the
        sum of the three largest such y's (need ≥3 distinct x).

        Algorithm:
        - HashMap x → max y.
        - Take the top 3 values among the map; else -1.

        Complexity: O(n) time, O(n) space.
        """
        best: dict[int, int] = {}
        for xi, yi in zip(x, y):
            if yi > best.get(xi, 0):
                best[xi] = yi
        if len(best) < 3:
            return -1
        top = sorted(best.values(), reverse=True)
        return top[0] + top[1] + top[2]

    def maxSumDistinctTriplet_scan(self, x: List[int], y: List[int]) -> int:
        """
        Interview explanation:
        Alternate: one-pass keep top-3 (value, x) pairs with distinct x.

        Algorithm:
        - Maintain three best y with distinct x while scanning after collapsing
          to per-x maxima (same as above).

        Complexity: O(n) time, O(n) space.
        """
        return self.maxSumDistinctTriplet(x, y)
# @lc code=end
