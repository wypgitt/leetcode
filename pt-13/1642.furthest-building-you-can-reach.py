#
# @lc app=leetcode id=1642 lang=python3
#
# [1642] Furthest Building You Can Reach
#
# https://leetcode.com/problems/furthest-building-you-can-reach/description/
#
# algorithms
# Medium (51.07%)
# Likes:    6274
# Dislikes: 151
# Total Accepted:    278K
# Total Submissions: 545K
# Testcase Example:  "[4,2,7,6,9,14,12]"
#
# You are given an integer array heights representing the heights of buildings,
# some bricks, and some ladders.
#
# You start your journey from building 0 and move to the next building by
# possibly using bricks or ladders.
#
# While moving from building i to building i+1 (0-indexed),
#
# If the current building's height is greater than or equal to the next
# building's height, you do not need a ladder or bricks.
#
# If the current building's height is less than the next building's height, you
# can either use one ladder or (h[i+1] - h[i]) bricks.
#
# Return the furthest building index (0-indexed) you can reach if you use the
# given ladders and bricks optimally.
#
# Example 1:
#
# Input: heights = [4,2,7,6,9,14,12], bricks = 5, ladders = 1
# Output: 4
# Explanation: Starting at building 0, you can follow these steps:
# - Go to building 1 without using ladders nor bricks since 4 >= 2.
# - Go to building 2 using 5 bricks. You must use either bricks or ladders
# because 2 < 7.
# - Go to building 3 without using ladders nor bricks since 7 >= 6.
# - Go to building 4 using your only ladder. You must use either bricks or
# ladders because 6 < 9.
# It is impossible to go beyond building 4 because you do not have any more
# bricks or ladders.
#
# Example 2:
#
# Input: heights = [4,12,2,7,3,18,20,3,19], bricks = 10, ladders = 2
# Output: 7
#
# Example 3:
#
# Input: heights = [14,3,19,3], bricks = 17, ladders = 0
# Output: 3
#
# Constraints:
#
# 1 <= heights.length <= 10^5
#
# 1 <= heights[i] <= 10^6
#
# 0 <= bricks <= 10^9
#
# 0 <= ladders <= heights.length
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def furthestBuilding(self, heights: List[int], bricks: int, ladders: int) -> int:
        """
        Interview explanation:
        Climb; climbs need bricks or ladders. Prefer ladders for largest climbs:
        min-heap of climb sizes using ladders; when >ladders, replace smallest
        climb with bricks.

        Algorithm (min-heap):
        - For each positive climb push to heap; if len>ladders, pop smallest onto
          bricks; if bricks <0 stop.

        Complexity: O(n log ladders) time, O(ladders) space.
        """
        heap = []
        for i in range(len(heights) - 1):
            d = heights[i + 1] - heights[i]
            if d <= 0:
                continue
            heapq.heappush(heap, d)
            if len(heap) > ladders:
                bricks -= heapq.heappop(heap)
                if bricks < 0:
                    return i
        return len(heights) - 1

    def furthestBuilding_binary_search(self, heights: List[int], bricks: int, ladders: int) -> int:
        """
        Interview explanation:
        Alternate: binary search furthest index; check if climbs to that index
        feasible (use ladders on largest climbs, bricks on rest).

        Algorithm (binary search + sort):
        - ok(mid): collect positive diffs to mid; sort desc; skip first `ladders`;
          sum rest <= bricks.

        Complexity: O(n log n * log n) time.
        """
        n = len(heights)

        def ok(mid: int) -> bool:
            climbs = []
            for i in range(mid):
                d = heights[i + 1] - heights[i]
                if d > 0:
                    climbs.append(d)
            climbs.sort(reverse=True)
            need = sum(climbs[ladders:])
            return need <= bricks

        lo, hi = 0, n - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if ok(mid):
                lo = mid
            else:
                hi = mid - 1
        return lo
# @lc code=end
