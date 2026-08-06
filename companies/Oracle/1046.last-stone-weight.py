#
# @lc app=leetcode id=1046 lang=python3
#
# [1046] Last Stone Weight
#
# https://leetcode.com/problems/last-stone-weight/description/
#
# algorithms
# Easy (66.69%)
# Likes:    6747
# Dislikes: 156
# Total Accepted:    987K
# Total Submissions: 1.5M
# Testcase Example:  "[2,7,4,1,8,1]"
#
# You are given an array of integers stones where stones[i] is the weight of
# the i^th stone.
#
# We are playing a game with the stones. On each turn, we choose the heaviest
# two stones and smash them together. Suppose the heaviest two stones have
# weights x and y with x <= y. The result of this smash is:
#
# If x == y, both stones are destroyed, and
#
# If x != y, the stone of weight x is destroyed, and the stone of weight y has
# new weight y - x.
#
# At the end of the game, there is at most one stone left.
#
# Return the weight of the last remaining stone. If there are no stones left,
# return 0.
#
# Example 1:
#
# Input: stones = [2,7,4,1,8,1]
# Output: 1
# Explanation:
# We combine 7 and 8 to get 1 so the array converts to [2,4,1,1,1] then,
# we combine 2 and 4 to get 2 so the array converts to [2,1,1,1] then,
# we combine 2 and 1 to get 1 so the array converts to [1,1,1] then,
# we combine 1 and 1 to get 0 so the array converts to [1] then that's the
# value of the last stone.
#
# Example 2:
#
# Input: stones = [1]
# Output: 1
#
# Constraints:
#
# 1 <= stones.length <= 30
#
# 1 <= stones[i] <= 1000
#

# @lc code=start
import heapq
from typing import List


class Solution:
    def lastStoneWeight(self, stones: List[int]) -> int:
        """
        Interview explanation:
        Always smash the two heaviest stones. Max-heap (negate for Python
        min-heap): pop two, if unequal push difference; repeat until ≤1 left.

        Algorithm:
        - heap = [-s for s in stones]; heapify
        - While len>1: y=-heappop; x=-heappop; if y>x: push(-(y-x))
        - Return -heap[0] or 0

        Complexity: O(n log n) time, O(n) space.
        """
        heap = [-s for s in stones]
        heapq.heapify(heap)
        while len(heap) > 1:
            y = -heapq.heappop(heap)
            x = -heapq.heappop(heap)
            if y > x:
                heapq.heappush(heap, -(y - x))
        return -heap[0] if heap else 0

    def lastStoneWeight_sort(self, stones: List[int]) -> int:
        """
        Interview explanation:
        Alternate: repeatedly sort and smash last two until one or zero remain.

        Algorithm:
        - While len>1: sort; smash last two

        Complexity: O(n^2 log n) time, O(n) space.
        """
        stones = list(stones)
        while len(stones) > 1:
            stones.sort()
            y = stones.pop()
            x = stones.pop()
            if y > x:
                stones.append(y - x)
        return stones[0] if stones else 0
# @lc code=end
