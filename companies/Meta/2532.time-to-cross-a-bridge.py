#
# @lc app=leetcode id=2532 lang=python3
#
# [2532] Time to Cross a Bridge
#
# https://leetcode.com/problems/time-to-cross-a-bridge/description/
#
# algorithms
# Hard (44.36%)
# Likes:    126
# Dislikes: 226
# Total Accepted:    6K
# Total Submissions: 13.6K
# Testcase Example:  "1\n3\n[[1,1,2,1],[1,1,3,1],[1,1,4,1]]"
#
# There are k workers who want to move n boxes from the right (old) warehouse to
# the left (new) warehouse. You are given the two integers n and k, and a 2D
# integer array time of size k x 4 where time[i] = [right_i, pick_i, left_i,
# put_i].
#
# The warehouses are separated by a river and connected by a bridge. Initially,
# all k workers are waiting on the left side of the bridge. To move the boxes,
# the i^th worker can do the following:
#
#
# Cross the bridge to the right side in right_i minutes.
#
#
# Pick a box from the right warehouse in pick_i minutes.
#
#
# Cross the bridge to the left side in left_i minutes.
#
#
# Put the box into the left warehouse in put_i minutes.
#
# The i^th worker is less efficient than the j^th worker if either condition is
# met:
#
#
# left_i + right_i > left_j + right_j
#
#
# left_i + right_i == left_j + right_j and i > j
#
# The following rules regulate the movement of the workers through the bridge:
#
#
# Only one worker can use the bridge at a time.
#
#
# When the bridge is unused prioritize the least efficient worker (who have
# picked up the box) on the right side to cross. If not, prioritize the least
# efficient worker on the left side to cross.
#
#
# If enough workers have already been dispatched from the left side to pick up
# all the remaining boxes, no more workers will be sent from the left side.
#
# Return the elapsed minutes at which the last box reaches the left side of the
# bridge.
#
#
#
# Example 1:
#
# Input: n = 1, k = 3, time = [[1,1,2,1],[1,1,3,1],[1,1,4,1]]
#
# Output: 6
#
# Explanation:
#
# From 0 to 1 minutes: worker 2 crosses the bridge to the right.
# From 1 to 2 minutes: worker 2 picks up a box from the right warehouse.
# From 2 to 6 minutes: worker 2 crosses the bridge to the left.
# From 6 to 7 minutes: worker 2 puts a box at the left warehouse.
# The whole process ends after 7 minutes. We return 6 because the problem asks
# for the instance of time at which the last worker reaches the left side of the
# bridge.
#
# Example 2:
#
# Input: n = 3, k = 2, time = [[1,5,1,8],[10,10,10,10]]
#
# Output: 37
#
# Explanation:
#
# The last box reaches the left side at 37 seconds. Notice, how we do not put
# the last boxes down, as that would take more time, and they are already on the
# left with the workers.
#
#
#
# Constraints:
#
#
# 1 <= n, k <= 10^4
#
#
# time.length == k
#
#
# time[i].length == 4
#
#
# 1 <= left_i, pick_i, right_i, put_i <= 1000
#

# @lc code=start
from typing import List
import heapq
import math


class Solution:
    def findCrossingTime(self, n: int, k: int, time: List[List[int]]) -> int:
        """
        Interview explanation:
        k workers move n boxes across a one-lane bridge. Least efficient workers
        (largest right+left, then larger index) have priority; right side waiting
        with a box always goes before left side. Return time when the last box
        finishes crossing to the left (put time not required).

        Algorithm:
        - Max-heaps for waiting on left/right bridge (keyed by efficiency).
        - Min-heaps for workers busy picking/putting (ready time, index).
        - At current time, move ready workers onto bridge queues; then either
          let right cross, else left cross (if boxes remain), else jump time
          to the next ready worker.

        Complexity: O((n + k) log k) time, O(k) space.
        """
        # bridge heaps: (-(right+left), -i) so least efficient / largest i first
        left_bridge: list[tuple[int, int]] = []
        right_bridge: list[tuple[int, int]] = []
        left_busy: list[tuple[int, int]] = []   # (ready_time, i)
        right_busy: list[tuple[int, int]] = []

        for i, (right, _pick, left, _put) in enumerate(time):
            heapq.heappush(left_bridge, (-(right + left), -i))

        cur = 0
        remain = n
        while remain > 0 or right_bridge or right_busy:
            while left_busy and left_busy[0][0] <= cur:
                i = heapq.heappop(left_busy)[1]
                heapq.heappush(left_bridge, (-(time[i][0] + time[i][2]), -i))
            while right_busy and right_busy[0][0] <= cur:
                i = heapq.heappop(right_busy)[1]
                heapq.heappush(right_bridge, (-(time[i][0] + time[i][2]), -i))

            if right_bridge:
                i = -heapq.heappop(right_bridge)[1]
                cur += time[i][2]
                heapq.heappush(left_busy, (cur + time[i][3], i))
            elif left_bridge and remain > 0:
                i = -heapq.heappop(left_bridge)[1]
                cur += time[i][0]
                heapq.heappush(right_busy, (cur + time[i][1], i))
                remain -= 1
            else:
                nxt = math.inf
                if left_busy and remain > 0:
                    nxt = min(nxt, left_busy[0][0])
                if right_busy:
                    nxt = min(nxt, right_busy[0][0])
                cur = nxt

        return cur
# @lc code=end
