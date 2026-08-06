#
# @lc app=leetcode id=1182 lang=python3
#
# [1182] Shortest Distance to Target Color
#
# https://leetcode.com/problems/shortest-distance-to-target-color/description/
#
# algorithms
# Medium (56.53%)
# Likes:    539
# Dislikes: 22
# Total Accepted:    41.5K
# Total Submissions: 73.4K
# Testcase Example:  "[1,1,2,1,3,2,2,3,3]\n[[1,3],[2,2],[6,1]]"
#
#
# You are given an array colors, in which there are three colors: 1, 2 and
# 3.
#
# You are also given some queries. Each query consists of two integers i
# and c, return the shortest distance between the given index i and the
# target color c. If there is no solution return -1.
#
# Example 1:
#
# Input: colors = [1,1,2,1,3,2,2,3,3], queries = [[1,3],[2,2],[6,1]]
# Output: [3,0,3]
# Explanation:
# The nearest 3 from index 1 is at index 4 (3 steps away).
# The nearest 2 from index 2 is at index 2 itself (0 steps away).
# The nearest 1 from index 6 is at index 3 (3 steps away).
#
# Example 2:
#
# Input: colors = [1,2], queries = [[0,3]]
# Output: [-1]
# Explanation: There is no 3 in the array.
#
# Constraints:
#
# 1 <= colors.length <= 5*10^4
#
# 1 <= colors[i] <= 3
#
# 1 <= queries.length <= 5*10^4
#
# queries[i].length == 2
#
# 0 <= queries[i][0] < colors.length
#
# 1 <= queries[i][1] <= 3
#
# @lc code=start

import bisect
from collections import defaultdict
from typing import List


class Solution:
    def shortestDistanceColor(self, colors: List[int], queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Premium: colors in {1,2,3}. For query (i,c) find min |j-i| with
        colors[j]=c, else -1. Precompute indices per color; binary search
        nearest index for each query.

        Algorithm (precompute + binary search):
        - pos[c] = sorted list of indices with color c.
        - For (i,c): bisect_left in pos[c]; check neighbors for min distance.

        Complexity: O(n + q log n) time, O(n) space.
        """
        pos = defaultdict(list)
        for i, c in enumerate(colors):
            pos[c].append(i)

        ans = []
        for i, c in queries:
            arr = pos.get(c)
            if not arr:
                ans.append(-1)
                continue
            j = bisect.bisect_left(arr, i)
            best = float('inf')
            if j < len(arr):
                best = min(best, arr[j] - i)
            if j > 0:
                best = min(best, i - arr[j - 1])
            ans.append(best if best != float('inf') else -1)
        return ans

    def shortestDistanceColor_precompute(self, colors: List[int], queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Alternate: two-pass precompute nearest distance to each color at every
        index (left-to-right then right-to-left mins), then O(1) per query.

        Algorithm:
        - dist[i][c] = min steps from i to color c (INF if none).
        - L→R update last seen; R→L take min with right side.
        - Answer dist[i][c] or -1.

        Complexity: O(n + q) time, O(n) space.
        """
        n = len(colors)
        INF = 10**9
        dist = [[INF] * 4 for _ in range(n)]

        last = [-1, -1, -1, -1]
        for i in range(n):
            last[colors[i]] = i
            for c in (1, 2, 3):
                if last[c] != -1:
                    dist[i][c] = i - last[c]

        last = [-1, -1, -1, -1]
        for i in range(n - 1, -1, -1):
            last[colors[i]] = i
            for c in (1, 2, 3):
                if last[c] != -1:
                    dist[i][c] = min(dist[i][c], last[c] - i)

        ans = []
        for i, c in queries:
            d = dist[i][c]
            ans.append(d if d < INF else -1)
        return ans
# @lc code=end
