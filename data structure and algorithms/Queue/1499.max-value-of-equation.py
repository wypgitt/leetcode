#
# @lc app=leetcode id=1499 lang=python3
#
# [1499] Max Value of Equation
#
# https://leetcode.com/problems/max-value-of-equation/description/
#
# algorithms
# Hard (45.16%)
# Likes:    1428
# Dislikes: 63
# Total Accepted:    57.3K
# Total Submissions: 127K
# Testcase Example:  "[[1,3],[2,0],[5,10],[6,-10]]"
#
# You are given an array points containing the coordinates of points on a 2D
# plane, sorted by the x-values, where points[i] = [x_i, y_i] such that x_i <
# x_j for all 1 <= i < j <= points.length. You are also given an integer k.
#
# Return the maximum value of the equation y_i + y_j + |x_i - x_j| where |x_i -
# x_j| <= k and 1 <= i < j <= points.length.
#
# It is guaranteed that there exists at least one pair of points that satisfy
# the constraint |x_i - x_j| <= k.
#
# Example 1:
#
# Input: points = [[1,3],[2,0],[5,10],[6,-10]], k = 1
# Output: 4
# Explanation: The first two points satisfy the condition |x_i - x_j| <= 1 and
# if we calculate the equation we get 3 + 0 + |1 - 2| = 4. Third and fourth
# points also satisfy the condition and give a value of 10 + -10 + |5 - 6| = 1.
# No other pairs satisfy the condition, so we return the max of 4 and 1.
#
# Example 2:
#
# Input: points = [[0,0],[3,0],[9,2]], k = 3
# Output: 3
# Explanation: Only the first two points have an absolute difference of 3 or
# less in the x-values, and give the value of 0 + 0 + |0 - 3| = 3.
#
# Constraints:
#
# 2 <= points.length <= 10^5
#
# points[i].length == 2
#
# -10^8 <= x_i, y_i <= 10^8
#
# 0 <= k <= 2 * 10^8
#
# x_i < x_j for all 1 <= i < j <= points.length
#
# x_i form a strictly increasing sequence.
#

# @lc code=start
from typing import List
from collections import deque


class Solution:
    def findMaxValueOfEquation(self, points: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Maximize yi+yj+|xi-xj| with |xi-xj|<=k. Points sorted by x, so
        = yi+yj+xj-xi = (yj+xj) + (yi-xi). For each j, maximize yi-xi among
        i with xj-xi<=k. Monotonic deque of (xi, yi-xi).

        Algorithm:
        - Deque decreasing by yi-xi; pop front if x out of window; update ans
          with yj+xj + front; push (xj, yj-xj) maintaining mono.

        Complexity: O(n) time, O(n) space.
        """
        dq = deque()  # (x, y-x)
        ans = float("-inf")
        for x, y in points:
            while dq and x - dq[0][0] > k:
                dq.popleft()
            if dq:
                ans = max(ans, y + x + dq[0][1])
            val = y - x
            while dq and dq[-1][1] <= val:
                dq.pop()
            dq.append((x, val))
        return int(ans)

    def findMaxValueOfEquation_heap(self, points: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Alternate: max-heap of (yi-xi, xi); pop stale; same formula.

        Algorithm:
        - heapq with (-(y-x), x); while heap and x-xi>k pop; update; push.

        Complexity: O(n log n) time, O(n) space.
        """
        import heapq

        heap = []
        ans = float("-inf")
        for x, y in points:
            while heap and x + heap[0][1] > k:
                heapq.heappop(heap)
            if heap:
                ans = max(ans, y + x - heap[0][0])
            heapq.heappush(heap, (-(y - x), -x))
        return int(ans)
# @lc code=end
