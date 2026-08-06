#
# @lc app=leetcode id=373 lang=python3
#
# [373] Find K Pairs with Smallest Sums
#
# https://leetcode.com/problems/find-k-pairs-with-smallest-sums/description/
#
# algorithms
# Medium (42.2%)
# Likes:    7060
# Dislikes: 500
# Total Accepted:    484K
# Total Submissions: 1.1M
# Testcase Example:  "[1,7,11]"
#
# You are given two integer arrays nums1 and nums2 sorted in non-decreasing
# order and an integer k.
#
# Define a pair (u, v) which consists of one element from the first array and
# one element from the second array.
#
# Return the k pairs (u_1, v_1), (u_2, v_2), ..., (u_k, v_k) with the smallest
# sums.
#
# Example 1:
#
# Input: nums1 = [1,7,11], nums2 = [2,4,6], k = 3
# Output: [[1,2],[1,4],[1,6]]
# Explanation: The first 3 pairs are returned from the sequence:
# [1,2],[1,4],[1,6],[7,2],[7,4],[11,2],[7,6],[11,4],[11,6]
#
# Example 2:
#
# Input: nums1 = [1,1,2], nums2 = [1,2,3], k = 2
# Output: [[1,1],[1,1]]
# Explanation: The first 2 pairs are returned from the sequence:
# [1,1],[1,1],[1,2],[2,1],[1,2],[2,2],[1,3],[1,3],[2,3]
#
# Constraints:
#
# 1 <= nums1.length, nums2.length <= 10^5
#
# -10^9 <= nums1[i], nums2[i] <= 10^9
#
# nums1 and nums2 both are sorted in non-decreasing order.
#
# 1 <= k <= 10^4
#
# k <= nums1.length * nums2.length
#

# @lc code=start
import heapq
from typing import List


class Solution:
    def kSmallestPairs(self, nums1: List[int], nums2: List[int], k: int) -> List[List[int]]:
        """
        Interview explanation:
        Both arrays are sorted ascending. The smallest pair sums come from
        small indices. Use a min-heap of (sum, i, j); expand the next index
        in nums2 for each popped pair, and seed with (i, 0) for i in nums1.

        Algorithm:
        - Push (nums1[i]+nums2[0], i, 0) for i in 0..min(k,n)-1.
        - Pop k times: record [nums1[i], nums2[j]]; if j+1 < m push (i, j+1).

        Complexity: O(k log k) time, O(k) space (k ≤ n*m).
        """
        if not nums1 or not nums2 or k <= 0:
            return []
        n, m = len(nums1), len(nums2)
        heap = []
        for i in range(min(k, n)):
            heapq.heappush(heap, (nums1[i] + nums2[0], i, 0))
        ans = []
        while heap and len(ans) < k:
            _, i, j = heapq.heappop(heap)
            ans.append([nums1[i], nums2[j]])
            if j + 1 < m:
                heapq.heappush(heap, (nums1[i] + nums2[j + 1], i, j + 1))
        return ans
# @lc code=end
