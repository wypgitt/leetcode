#
# @lc app=leetcode id=1508 lang=python3
#
# [1508] Range Sum of Sorted Subarray Sums
#
# https://leetcode.com/problems/range-sum-of-sorted-subarray-sums/description/
#
# algorithms
# Medium (63.01%)
# Likes:    1617
# Dislikes: 270
# Total Accepted:    190K
# Total Submissions: 301K
# Testcase Example:  "[1,2,3,4]"
#
# You are given the array nums consisting of n positive integers. You computed
# the sum of all non-empty continuous subarrays from the array and then sorted
# them in non-decreasing order, creating a new array of n * (n + 1) / 2
# numbers.
#
# Return the sum of the numbers from index left to index right (indexed from
# 1), inclusive, in the new array. Since the answer can be a huge number return
# it modulo 10^9 + 7.
#
# Example 1:
#
# Input: nums = [1,2,3,4], n = 4, left = 1, right = 5
# Output: 13
# Explanation: All subarray sums are 1, 3, 6, 10, 2, 5, 9, 3, 7, 4. After
# sorting them in non-decreasing order we have the new array [1, 2, 3, 3, 4, 5,
# 6, 7, 9, 10]. The sum of the numbers from index le = 1 to ri = 5 is 1 + 2 + 3
# + 3 + 4 = 13.
#
# Example 2:
#
# Input: nums = [1,2,3,4], n = 4, left = 3, right = 4
# Output: 6
# Explanation: The given array is the same as example 1. We have the new array
# [1, 2, 3, 3, 4, 5, 6, 7, 9, 10]. The sum of the numbers from index le = 3 to
# ri = 4 is 3 + 3 = 6.
#
# Example 3:
#
# Input: nums = [1,2,3,4], n = 4, left = 1, right = 10
# Output: 50
#
# Constraints:
#
# n == nums.length
#
# 1 <= nums.length <= 1000
#
# 1 <= nums[i] <= 100
#
# 1 <= left <= right <= n * (n + 1) / 2
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def rangeSum(self, nums: List[int], n: int, left: int, right: int) -> int:
        """
        Interview explanation:
        Form all contiguous subarray sums, sort them, return sum of the
        inclusive sorted range [left,right] (1-indexed) mod 1e9+7.
        n<=1000 ⇒ O(n^2) subarrays is acceptable.

        Algorithm:
        - Nested loop accumulate subarray sums; sort; sum slice [left-1:right].

        Complexity: O(n^2 log n) time, O(n^2) space.
        """
        MOD = 10**9 + 7
        sums = []
        for i in range(n):
            s = 0
            for j in range(i, n):
                s += nums[j]
                sums.append(s)
        sums.sort()
        return sum(sums[left - 1 : right]) % MOD

    def rangeSum_heap(self, nums: List[int], n: int, left: int, right: int) -> int:
        """
        Interview explanation:
        Alternate: min-heap of (subarray_sum, end_index) expanding subarrays
        like merging; pop left-1 times then sum next (right-left+1) values.
        Useful when discussing top-k without storing all sums (still O(n^2) worst).

        Algorithm:
        - Push (nums[i], i) for all i; pop: push (sum+nums[end+1], end+1) if ok.

        Complexity: O(right log n) time with heap size O(n), O(n) space.
        """
        MOD = 10**9 + 7
        heap = [(nums[i], i) for i in range(n)]
        heapq.heapify(heap)
        ans = 0
        for cnt in range(1, right + 1):
            val, end = heapq.heappop(heap)
            if cnt >= left:
                ans = (ans + val) % MOD
            if end + 1 < n:
                heapq.heappush(heap, (val + nums[end + 1], end + 1))
        return ans
# @lc code=end
