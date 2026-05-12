#
# @lc app=leetcode id=1057 lang=python3
#
# [1057] Campus Bikes
#
# https://leetcode.com/problems/campus-bikes/description/
#
# algorithms
# Medium (59.08%)
# Likes:    1002
# Dislikes: 199
# Total Accepted:    78.2K
# Total Submissions: 132.4K
# Testcase Example:  '[[0,0],[2,1]]\n[[1,2],[3,3]]'
#
# On a campus represented on the X-Y plane, there are n workers and m bikes,
# with n <= m.
# 
# You are given an array workers of length n where workers[i] = [xi, yi] is the
# position of the i^th worker. You are also given an array bikes of length m
# where bikes[j] = [xj, yj] is the position of the j^th bike. All the given
# positions are unique.
# 
# Assign a bike to each worker. Among the available bikes and workers, we
# choose the (workeri, bikej) pair with the shortest Manhattan distance between
# each other and assign the bike to that worker.
# 
# If there are multiple (workeri, bikej) pairs with the same shortest Manhattan
# distance, we choose the pair with the smallest worker index. If there are
# multiple ways to do that, we choose the pair with the smallest bike index.
# Repeat this process until there are no available workers.
# 
# Return an array answer of length n, where answer[i] is the index (0-indexed)
# of the bike that the i^th worker is assigned to.
# 
# The Manhattan distance between two points p1 and p2 is Manhattan(p1, p2) =
# |p1.x - p2.x| + |p1.y - p2.y|.
# 
# 
# Example 1:
# 
# 
# Input: workers = [[0,0],[2,1]], bikes = [[1,2],[3,3]]
# Output: [1,0]
# Explanation: Worker 1 grabs Bike 0 as they are closest (without ties), and
# Worker 0 is assigned Bike 1. So the output is [1, 0].
# 
# 
# Example 2:
# 
# 
# Input: workers = [[0,0],[1,1],[2,0]], bikes = [[1,0],[2,2],[2,1]]
# Output: [0,2,1]
# Explanation: Worker 0 grabs Bike 0 at first. Worker 1 and Worker 2 share the
# same distance to Bike 2, thus Worker 1 is assigned to Bike 2, and Worker 2
# will take Bike 1. So the output is [0,2,1].
# 
# 
# 
# Constraints:
# 
# 
# n == workers.length
# m == bikes.length
# 1 <= n <= m <= 1000
# workers[i].length == bikes[j].length == 2
# 0 <= xi, yi < 1000
# 0 <= xj, yj < 1000
# All worker and bike locations are unique.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def assignBikes(self, workers: List[List[int]], bikes: List[List[int]]) -> List[int]:
        max_distance = 2000
        buckets = [[] for _ in range(max_distance)]

        for worker_index, (wx, wy) in enumerate(workers):
            for bike_index, (bx, by) in enumerate(bikes):
                distance = abs(wx - bx) + abs(wy - by)
                buckets[distance].append((worker_index, bike_index))

        assignment = [-1] * len(workers)
        bike_used = [False] * len(bikes)
        assigned_workers = 0

        for pairs in buckets:
            for worker_index, bike_index in pairs:
                if assignment[worker_index] == -1 and not bike_used[bike_index]:
                    assignment[worker_index] = bike_index
                    bike_used[bike_index] = True
                    assigned_workers += 1

                    if assigned_workers == len(workers):
                        return assignment

        return assignment
# @lc code=end

"""
Interview Explanation

Core idea:
The assignment rule is global ordering by (distance, worker index, bike index).
Coordinates are less than 1000, so Manhattan distance is at most 1998. Bucket
sort lets us process pairs in exact required order without sorting one million
pairs by comparison.

Algorithm:
1. Create distance buckets.
2. Generate every worker-bike pair. Because workers and bikes are looped in
   increasing index order, pairs inside a bucket are already ordered by worker
   index then bike index.
3. Process buckets from smallest distance to largest.
4. Assign a pair if both the worker and bike are still available.
5. Stop once every worker has a bike.

Data structure choice:
Buckets exploit the small distance range. The assignment array tracks whether a
worker is done; a boolean array tracks used bikes.

Correctness:
The problem repeatedly chooses the available pair with the smallest distance,
then smallest worker index, then smallest bike index. Bucket iteration gives
increasing distance, and insertion order inside each bucket gives increasing
worker and bike indices. Skipping unavailable pairs exactly reflects previous
assignments. Therefore every chosen pair matches the required rule.

Complexity:
Let W be workers and B be bikes. Generating pairs costs O(WB), and bucket
processing also costs O(WB) in the worst case. Space is O(WB) for the buckets.

Tests and edge cases:
- Ties by distance are resolved by worker index, then bike index.
- More bikes than workers is normal; unused bikes remain False.
- One worker receives the nearest bike.
- Maximum coordinates still fit in bucket indices because max distance is 1998.
"""
