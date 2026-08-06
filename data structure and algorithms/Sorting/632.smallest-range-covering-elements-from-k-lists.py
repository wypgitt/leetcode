#
# @lc app=leetcode id=632 lang=python3
#
# [632] Smallest Range Covering Elements from K Lists
#
# https://leetcode.com/problems/smallest-range-covering-elements-from-k-lists/description/
#
# algorithms
# Hard (70.3%)
# Likes:    4459
# Dislikes: 103
# Total Accepted:    252K
# Total Submissions: 359K
# Testcase Example:  "[[4,10,15,24,26],[0,9,12,20],[5,18,22,30]]"
#
# You have k lists of sorted integers in non-decreasing order. Find the
# smallest range that includes at least one number from each of the k lists.
#
# We define the range [a, b] is smaller than range [c, d] if b - a < d - c or a
# < c if b - a == d - c.
#
# Example 1:
#
# Input: nums = [[4,10,15,24,26],[0,9,12,20],[5,18,22,30]]
# Output: [20,24]
# Explanation:
# List 1: [4, 10, 15, 24,26], 24 is in range [20,24].
# List 2: [0, 9, 12, 20], 20 is in range [20,24].
# List 3: [5, 18, 22, 30], 22 is in range [20,24].
#
# Example 2:
#
# Input: nums = [[1,2,3],[1,2,3],[1,2,3]]
# Output: [1,1]
#
# Constraints:
#
# nums.length == k
#
# 1 <= k <= 3500
#
# 1 <= nums[i].length <= 50
#
# -10^5 <= nums[i][j] <= 10^5
#
# nums[i] is sorted in non-decreasing order.
#

# @lc code=start

import heapq
from typing import List


class Solution:
    def smallestRange(self, nums: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Find smallest closed range covering at least one number from each of k
        sorted lists. Maintain a min-heap of current heads + running max.

        Algorithm:
        - Push (nums[i][0], i, 0) for each list; track cur_max.
        - Pop min; update best range [min, cur_max]; push next from same list;
          update cur_max. Stop when a list is exhausted.

        Complexity: O(N log k) time, O(k) space (N = total elements).
        """
        heap = []
        cur_max = float("-inf")
        for i, arr in enumerate(nums):
            heapq.heappush(heap, (arr[0], i, 0))
            cur_max = max(cur_max, arr[0])
        best = [float("-inf"), float("inf")]
        while True:
            cur_min, i, j = heapq.heappop(heap)
            if cur_max - cur_min < best[1] - best[0] or (
                cur_max - cur_min == best[1] - best[0] and cur_min < best[0]
            ):
                best = [cur_min, cur_max]
            if j + 1 == len(nums[i]):
                return best
            nxt = nums[i][j + 1]
            heapq.heappush(heap, (nxt, i, j + 1))
            cur_max = max(cur_max, nxt)
# @lc code=end
