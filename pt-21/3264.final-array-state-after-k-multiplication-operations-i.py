#
# @lc app=leetcode id=3264 lang=python3
#
# [3264] Final Array State After K Multiplication Operations I
#
# https://leetcode.com/problems/final-array-state-after-k-multiplication-operations-i/description/
#
# algorithms
# Easy (86.93%)
# Likes:    567
# Dislikes: 13
# Total Accepted:    211.9K
# Total Submissions: 243.7K
# Testcase Example:  "[2,1,3,5,6]\n5\n2"
#
#
# You are given an integer array nums, an integer k, and an integer
# multiplier.
#
# You need to perform k operations on nums. In each operation:
#
# Find the minimum value x in nums. If there are multiple occurrences of
# the minimum value, select the one that appears first.
#
# Replace the selected minimum value x with x * multiplier.
#
# Return an integer array denoting the final state of nums after
# performing all k operations.
#
# Example 1:
#
# Input: nums = [2,1,3,5,6], k = 5, multiplier = 2
#
# Output: [8,4,6,5,6]
#
# Explanation:
#
#                         Operation
#                         Result
#
#                         After operation 1
#                         [2, 2, 3, 5, 6]
#
#                         After operation 2
#                         [4, 2, 3, 5, 6]
#
#                         After operation 3
#                         [4, 4, 3, 5, 6]
#
#                         After operation 4
#                         [4, 4, 6, 5, 6]
#
#                         After operation 5
#                         [8, 4, 6, 5, 6]
#
# Example 2:
#
# Input: nums = [1,2], k = 3, multiplier = 4
#
# Output: [16,8]
#
# Explanation:
#
#                         Operation
#                         Result
#
#                         After operation 1
#                         [4, 2]
#
#                         After operation 2
#                         [4, 8]
#
#                         After operation 3
#                         [16, 8]
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 1 <= nums[i] <= 100
#
# 1 <= k <= 10
#
# 1 <= multiplier <= 5
#

# @lc code=start

from typing import List
import heapq


class Solution:
    def getFinalState(self, nums: List[int], k: int, multiplier: int) -> List[int]:
        """
        Interview explanation:
        Each operation multiplies the current minimum (leftmost on ties). With
        tiny k, simulate with a min-heap of (value, index).

        Algorithm:
        - Heapify (nums[i], i); k times pop, multiply, push.
        - Write final heap values back into the array by index.

        Complexity: O((n + k) log n) time, O(n) space.
        """
        h = [(v, i) for i, v in enumerate(nums)]
        heapq.heapify(h)
        for _ in range(k):
            v, i = heapq.heappop(h)
            heapq.heappush(h, (v * multiplier, i))
        ans = [0] * len(nums)
        for v, i in h:
            ans[i] = v
        return ans

    def getFinalState_scan(self, nums: List[int], k: int, multiplier: int) -> List[int]:
        """
        Interview explanation:
        Alternate for n,k ≤ 100: linear scan for the min index each operation.

        Algorithm:
        - k times: i = argmin; nums[i] *= multiplier.

        Complexity: O(n * k) time, O(1) extra space.
        """
        a = nums[:]
        for _ in range(k):
            i = 0
            for j in range(1, len(a)):
                if a[j] < a[i]:
                    i = j
            a[i] *= multiplier
        return a
# @lc code=end
