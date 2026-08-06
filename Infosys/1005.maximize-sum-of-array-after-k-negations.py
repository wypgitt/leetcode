#
# @lc app=leetcode id=1005 lang=python3
#
# [1005] Maximize Sum Of Array After K Negations
#
# https://leetcode.com/problems/maximize-sum-of-array-after-k-negations/description/
#
# algorithms
# Easy (54.16%)
# Likes:    1748
# Dislikes: 127
# Total Accepted:    147K
# Total Submissions: 272K
# Testcase Example:  "[4,2,3]"
#
# Given an integer array nums and an integer k, modify the array in the
# following way:
#
# choose an index i and replace nums[i] with -nums[i].
#
# You should apply this process exactly k times. You may choose the same index
# i multiple times.
#
# Return the largest possible sum of the array after modifying it in this way.
#
# Example 1:
#
# Input: nums = [4,2,3], k = 1
# Output: 5
# Explanation: Choose index 1 and nums becomes [4,-2,3].
#
# Example 2:
#
# Input: nums = [3,-1,0,2], k = 3
# Output: 6
# Explanation: Choose indices (1, 2, 2) and nums becomes [3,1,0,2].
#
# Example 3:
#
# Input: nums = [2,-3,-1,5,-4], k = 2
# Output: 13
# Explanation: Choose indices (1, 4) and nums becomes [2,3,-1,5,4].
#
# Constraints:
#
# 1 <= nums.length <= 10^4
#
# -100 <= nums[i] <= 100
#
# 1 <= k <= 10^4
#

# @lc code=start
import heapq
from typing import List


class Solution:
    def largestSumAfterKNegations(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Greedily flip the smallest (most negative) numbers first using a min-heap.
        After negatives are gone, if k is odd flip the current smallest absolute.

        Algorithm:
        - Heapify nums; while k>0: pop min, push -min, k--
        - Return sum(heap)

        Complexity: O(n + k log n) time, O(n) space.
        """
        heapq.heapify(nums)
        for _ in range(k):
            heapq.heappush(nums, -heapq.heappop(nums))
        return sum(nums)

    def largestSumAfterKNegations_sort(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate classic: sort ascending; flip negatives from left while k>0;
        if k remains odd, flip the smallest absolute value once.

        Algorithm:
        - Sort; flip negatives left-to-right
        - If k odd: subtract 2*min(abs) from sum (equiv. flip smallest)

        Complexity: O(n log n) time, O(n) space for sort.
        """
        nums.sort()
        i = 0
        n = len(nums)
        while k > 0 and i < n and nums[i] < 0:
            nums[i] = -nums[i]
            k -= 1
            i += 1
        if k % 2 == 1:
            m = min(nums)
            return sum(nums) - 2 * m
        return sum(nums)
# @lc code=end
