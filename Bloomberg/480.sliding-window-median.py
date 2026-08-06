#
# @lc app=leetcode id=480 lang=python3
#
# [480] Sliding Window Median
#
# https://leetcode.com/problems/sliding-window-median/description/
#
# algorithms
# Hard (39.07%)
# Likes:    3633
# Dislikes: 244
# Total Accepted:    228K
# Total Submissions: 582K
# Testcase Example:  "[1,3,-1,-3,5,3,6,7]"
#
# The median is the middle value in an ordered integer list. If the size of the
# list is even, there is no middle value. So the median is the mean of the two
# middle values.
#
# For examples, if arr = [2,3,4], the median is 3.
#
# For examples, if arr = [1,2,3,4], the median is (2 + 3) / 2 = 2.5.
#
# You are given an integer array nums and an integer k. There is a sliding
# window of size k which is moving from the very left of the array to the very
# right. You can only see the k numbers in the window. Each time the sliding
# window moves right by one position.
#
# Return the median array for each window in the original array. Answers within
# 10^-5 of the actual value will be accepted.
#
# Example 1:
#
# Input: nums = [1,3,-1,-3,5,3,6,7], k = 3
# Output: [1.00000,-1.00000,-1.00000,3.00000,5.00000,6.00000]
# Explanation:
# Window position Median
# --------------- -----
# [1 3 -1] -3 5 3 6 7 1
# 1 [3 -1 -3] 5 3 6 7 -1
# 1 3 [-1 -3 5] 3 6 7 -1
# 1 3 -1 [-3 5 3] 6 7 3
# 1 3 -1 -3 [5 3 6] 7 5
# 1 3 -1 -3 5 [3 6 7] 6
#
# Example 2:
#
# Input: nums = [1,2,3,4,2,3,1,4,2], k = 3
# Output: [2.00000,3.00000,3.00000,3.00000,2.00000,3.00000,2.00000]
#
# Constraints:
#
# 1 <= k <= nums.length <= 10^5
#
# -2^31 <= nums[i] <= 2^31 - 1
#

# @lc code=start
import heapq
from collections import defaultdict
from typing import List


class Solution:
    def medianSlidingWindow(self, nums: List[int], k: int) -> List[float]:
        """
        Interview explanation:
        Two heaps maintain the window median: max-heap `low` (lower half) and
        min-heap `high` (upper half), kept size-balanced. Lazy deletion removes
        elements that slide out without scanning the heaps.

        Algorithm:
        - add(num): push to low or high; rebalance sizes (lo = hi or lo = hi+1).
        - remove(num): mark in delayed; decrement size; prune tops if delayed.
        - median: -low[0] if k odd else average of tops.

        Complexity: O(n log k) amortized time, O(k) space.
        """
        low: List[int] = []  # max-heap via negation
        high: List[int] = []  # min-heap
        delayed: dict = defaultdict(int)
        lo_size = hi_size = 0

        def prune(heap: List[int], is_low: bool) -> None:
            while heap:
                x = -heap[0] if is_low else heap[0]
                if delayed[x]:
                    delayed[x] -= 1
                    if delayed[x] == 0:
                        del delayed[x]
                    heapq.heappop(heap)
                else:
                    break

        def rebalance() -> None:
            nonlocal lo_size, hi_size
            if lo_size > hi_size + 1:
                heapq.heappush(high, -heapq.heappop(low))
                lo_size -= 1
                hi_size += 1
                prune(low, True)
            elif lo_size < hi_size:
                heapq.heappush(low, -heapq.heappop(high))
                hi_size -= 1
                lo_size += 1
                prune(high, False)

        def add(num: int) -> None:
            nonlocal lo_size, hi_size
            if not low or num <= -low[0]:
                heapq.heappush(low, -num)
                lo_size += 1
            else:
                heapq.heappush(high, num)
                hi_size += 1
            rebalance()

        def remove(num: int) -> None:
            nonlocal lo_size, hi_size
            delayed[num] += 1
            if num <= -low[0]:
                lo_size -= 1
                if num == -low[0]:
                    prune(low, True)
            else:
                hi_size -= 1
                if high and num == high[0]:
                    prune(high, False)
            rebalance()

        def get_median() -> float:
            prune(low, True)
            prune(high, False)
            if k & 1:
                return float(-low[0])
            return (-low[0] + high[0]) / 2.0

        ans: List[float] = []
        for i, num in enumerate(nums):
            add(num)
            if i >= k - 1:
                ans.append(get_median())
                remove(nums[i - k + 1])
        return ans
# @lc code=end
