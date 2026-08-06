#
# @lc app=leetcode id=3478 lang=python3
#
# [3478] Choose K Elements With Maximum Sum
#
# https://leetcode.com/problems/choose-k-elements-with-maximum-sum/description/
#
# algorithms
# Medium (34.20%)
# Likes:    192
# Dislikes: 9
# Total Accepted:    21.4K
# Total Submissions: 62.6K
# Testcase Example:  "[4,2,1,5,3]\n[10,20,30,40,50]\n2"
#
#
# You are given two integer arrays, nums1 and nums2, both of length n,
# along with a positive integer k.
#
# For each index i from 0 to n - 1, perform the following:
#
# Find all indices j where nums1[j] is less than nums1[i].
#
# Choose at most k values of nums2[j] at these indices to maximize the
# total sum.
#
# Return an array answer of size n, where answer[i] represents the result
# for the corresponding index i.
#
# Example 1:
#
# Input: nums1 = [4,2,1,5,3], nums2 = [10,20,30,40,50], k = 2
#
# Output: [80,30,0,80,50]
#
# Explanation:
#
# For i = 0: Select the 2 largest values from nums2 at indices [1, 2, 4]
# where nums1[j] < nums1[0], resulting in 50 + 30 = 80.
#
# For i = 1: Select the 2 largest values from nums2 at index [2] where
# nums1[j] < nums1[1], resulting in 30.
#
# For i = 2: No indices satisfy nums1[j] < nums1[2], resulting in 0.
#
# For i = 3: Select the 2 largest values from nums2 at indices [0, 1, 2,
# 4] where nums1[j] < nums1[3], resulting in 50 + 30 = 80.
#
# For i = 4: Select the 2 largest values from nums2 at indices [1, 2]
# where nums1[j] < nums1[4], resulting in 30 + 20 = 50.
#
# Example 2:
#
# Input: nums1 = [2,2,2,2], nums2 = [3,1,2,3], k = 1
#
# Output: [0,0,0,0]
#
# Explanation:
#
# Since all elements in nums1 are equal, no indices satisfy the condition
# nums1[j] < nums1[i] for any i, resulting in 0 for all positions.
#
# Constraints:
#
# n == nums1.length == nums2.length
#
# 1 <= n <= 10^5
#
# 1 <= nums1[i], nums2[i] <= 10^6
#
# 1 <= k <= n
#

# @lc code=start
import heapq
import itertools
from typing import List


class Solution:
    def findMaxSum(self, nums1: List[int], nums2: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        Process indices in increasing nums1 order. Maintain the top-k nums2
        values among strictly smaller nums1 so far via a min-heap.

        Algorithm:
        - Sort (nums1[i], i). For equal nums1, reuse previous answer.
        - Otherwise answer is current heap sum; then insert nums2[i], trim to k.

        Complexity: O(n log n) time, O(n + k) space.
        """
        n = len(nums1)
        ans = [0] * n
        order = sorted((num, i) for i, num in enumerate(nums1))
        min_heap: List[int] = []
        first = order[0][1]
        heapq.heappush(min_heap, nums2[first])
        total = nums2[first]

        for (prev_num, prev_i), (curr_num, curr_i) in itertools.pairwise(order):
            if curr_num == prev_num:
                ans[curr_i] = ans[prev_i]
            else:
                ans[curr_i] = total
            heapq.heappush(min_heap, nums2[curr_i])
            total += nums2[curr_i]
            if len(min_heap) == k + 1:
                total -= heapq.heappop(min_heap)
        return ans
# @lc code=end

