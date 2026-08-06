#
# @lc app=leetcode id=973 lang=python3
#
# [973] K Closest Points to Origin
#
# https://leetcode.com/problems/k-closest-points-to-origin/description/
#
# algorithms
# Medium (69.24%)
# Likes:    9180
# Dislikes: 340
# Total Accepted:    1.8M
# Total Submissions: 2.6M
# Testcase Example:  "[[1,3],[-2,2]]"
#
# Given an array of points where points[i] = [x_i, y_i] represents a point on
# the X-Y plane and an integer k, return the k closest points to the origin (0,
# 0).
#
# The distance between two points on the X-Y plane is the Euclidean distance
# (i.e., √(x_1 - x_2)^2 + (y_1 - y_2)^2).
#
# You may return the answer in any order. The answer is guaranteed to be unique
# (except for the order that it is in).
#
# Example 1:
#
# Input: points = [[1,3],[-2,2]], k = 1
# Output: [[-2,2]]
# Explanation:
# The distance between (1, 3) and the origin is sqrt(10).
# The distance between (-2, 2) and the origin is sqrt(8).
# Since sqrt(8) < sqrt(10), (-2, 2) is closer to the origin.
# We only want the closest k = 1 points from the origin, so the answer is just
# [[-2,2]].
#
# Example 2:
#
# Input: points = [[3,3],[5,-1],[-2,4]], k = 2
# Output: [[3,3],[-2,4]]
# Explanation: The answer [[-2,4],[3,3]] would also be accepted.
#
# Constraints:
#
# 1 <= k <= points.length <= 10^4
#
# -10^4 <= x_i, y_i <= 10^4
#

# @lc code=start
import heapq
import random
from typing import List


class Solution:
    def kClosest(self, points: List[List[int]], k: int) -> List[List[int]]:
        """
        Interview explanation:
        Keep a max-heap of size k keyed by squared distance; discard farther
        points. Squared distance avoids sqrt and preserves order.

        Algorithm (max-heap of size k):
        - Push (-dist^2, x, y); if heap grows past k, pop farthest.
        - Return the k points remaining in the heap.

        Complexity: O(n log k) time, O(k) space.
        """
        heap: List[tuple] = []
        for x, y in points:
            dist = x * x + y * y
            heapq.heappush(heap, (-dist, x, y))
            if len(heap) > k:
                heapq.heappop(heap)
        return [[x, y] for _, x, y in heap]

    def kClosest_sort(self, points: List[List[int]], k: int) -> List[List[int]]:
        """
        Interview explanation:
        Alternate classic: sort all points by squared distance ascending and
        take the first k.

        Algorithm:
        - Sort points by x^2 + y^2; return points[:k].

        Complexity: O(n log n) time, O(n) space (sort).
        """
        points.sort(key=lambda p: p[0] * p[0] + p[1] * p[1])
        return points[:k]

    def kClosest_quickselect(self, points: List[List[int]], k: int) -> List[List[int]]:
        """
        Interview explanation:
        Alternate optimal average: quickselect partition so the k closest sit
        in the first k positions (order among them need not be sorted).

        Algorithm:
        - dist(i) = x^2+y^2. Partition around a random pivot until left side
          has exactly k elements (or more then shrink hi, else grow lo).
        - Return points[:k].

        Complexity: O(n) average / O(n^2) worst time, O(1) extra space.
        """
        def dist(i: int) -> int:
            x, y = points[i]
            return x * x + y * y

        def partition(lo: int, hi: int) -> int:
            pivot = random.randint(lo, hi)
            points[pivot], points[hi] = points[hi], points[pivot]
            store = lo
            pd = dist(hi)
            for i in range(lo, hi):
                if dist(i) < pd:
                    points[store], points[i] = points[i], points[store]
                    store += 1
            points[store], points[hi] = points[hi], points[store]
            return store

        lo, hi = 0, len(points) - 1
        while lo <= hi:
            p = partition(lo, hi)
            if p == k - 1:
                break
            if p < k - 1:
                lo = p + 1
            else:
                hi = p - 1
        return points[:k]
# @lc code=end
