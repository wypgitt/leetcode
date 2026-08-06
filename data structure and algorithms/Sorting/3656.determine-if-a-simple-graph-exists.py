#
# @lc app=leetcode id=3656 lang=python3
#
# [3656] Determine if a Simple Graph Exists
#
# https://leetcode.com/problems/determine-if-a-simple-graph-exists/description/
#
# algorithms
# Medium (47.23%)
# Likes:    9
# Dislikes: 8
# Total Accepted:    468
# Total Submissions: 991
# Testcase Example:  "[3,1,2,2]"
#
#
# You are given an integer array degrees, where degrees[i] represents the
# desired degree of the i^th vertex.
#
# Your task is to determine if there exists an undirected simple graph
# with exactly these vertex degrees.
#
# A simple graph has no self-loops or parallel edges between the same pair
# of vertices.
#
# Return true if such a graph exists, otherwise return false.
#
# Example 1:
#
# Input: degrees = [3,1,2,2]
#
# Output: true
#
# Explanation:
#
# ​​​​​​​
#
# One possible undirected simple graph is:
#
# Edges: (0, 1), (0, 2), (0, 3), (2, 3)
#
# Degrees: deg(0) = 3, deg(1) = 1, deg(2) = 2, deg(3) = 2.
#
# Example 2:
#
# Input: degrees = [1,3,3,1]
#
# Output: false
#
# Explanation:​​​​​​​
#
# degrees[1] = 3 and degrees[2] = 3 means they must be connected to all
# other vertices.
#
# This requires degrees[0] and degrees[3] to be at least 2, but both are
# equal to 1, which contradicts the requirement.
#
# Thus, the answer is false.
#
# Constraints:
#
# 1 <= n == degrees.length <= 10^​​​​​​​5
#
# 0 <= degrees[i] <= n - 1
#

# @lc code=start
from typing import List


class Solution:
    def simpleGraphExists(self, degrees: List[int]) -> bool:
        """
        Interview explanation:
        Graphic sequences of simple graphs are characterized by the
        Erdős–Gállai inequalities (plus even degree sum).

        Algorithm:
        - Sort degrees descending; reject odd sum.
        - For each k, Σ d[0..k) ≤ k(k-1) + Σ_{i≥k} min(d[i], k), using
          prefix sums and a pointer over the d[i] ≥ k region.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(degrees)
        d = sorted(degrees, reverse=True)
        if sum(d) % 2:
            return False
        pref = [0]
        for x in d:
            pref.append(pref[-1] + x)
        j = n
        for k in range(1, n + 1):
            while j > 0 and d[j - 1] < k:
                j -= 1
            if j > k:
                right = (j - k) * k + (pref[n] - pref[j])
            else:
                right = pref[n] - pref[k]
            if pref[k] > k * (k - 1) + right:
                return False
        return True
# @lc code=end

