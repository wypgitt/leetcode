#
# @lc app=leetcode id=2386 lang=python3
#
# [2386] Find the K-Sum of an Array
#
# https://leetcode.com/problems/find-the-k-sum-of-an-array/description/
#
# algorithms
# Hard (41.70%)
# Likes:    620
# Dislikes: 27
# Total Accepted:    14.7K
# Total Submissions: 35.3K
# Testcase Example:  "[2,4,-2]\n5"
#
# You are given an integer array nums and a positive integer k. You can choose
# any subsequence of the array and sum all of its elements together.
#
# We define the K-Sum of the array as the k^th largest subsequence sum that can
# be obtained (not necessarily distinct).
#
# Return the K-Sum of the array.
#
# A subsequence is an array that can be derived from another array by deleting
# some or no elements without changing the order of the remaining elements.
#
# Note that the empty subsequence is considered to have a sum of 0.
#
#
#
# Example 1:
#
# Input: nums = [2,4,-2], k = 5
# Output: 2
# Explanation: All the possible subsequence sums that we can obtain are the
# following sorted in decreasing order:
# 6, 4, 4, 2, 2, 0, 0, -2.
# The 5-Sum of the array is 2.
#
# Example 2:
#
# Input: nums = [1,-2,3,4,-10,12], k = 16
# Output: 10
# Explanation: The 16-Sum of the array is 10.
#
#
#
# Constraints:
#
#
# n == nums.length
#
#
# 1 <= n <= 10^5
#
#
# -10^9 <= nums[i] <= 10^9
#
#
# 1 <= k <= min(2000, 2^n)
#

# @lc code=start

from typing import List
import heapq


class Solution:
    def kSum(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        k-sum = k-th largest subsequence sum (empty subsequence sum is 0).

        Algorithm:
        - max_sum = sum of positives. The k-th largest = max_sum minus the
          (k-1)-th smallest sum of a "reduction" built from sorted abs values
          via a Dijkstra-like heap expansion.

        Complexity: O(n log n + k log k) time, O(n + k) space.
        """
        max_sum = sum(x for x in nums if x > 0)
        if k == 1:
            return max_sum
        arr = sorted(abs(x) for x in nums)
        n = len(arr)
        h = [(arr[0], 0)]
        cur = 0
        for _ in range(k - 1):
            cur, i = heapq.heappop(h)
            if i + 1 < n:
                heapq.heappush(h, (cur - arr[i] + arr[i + 1], i + 1))
                heapq.heappush(h, (cur + arr[i + 1], i + 1))
        return max_sum - cur
# @lc code=end
