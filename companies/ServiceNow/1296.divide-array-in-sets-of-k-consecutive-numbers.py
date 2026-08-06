#
# @lc app=leetcode id=1296 lang=python3
#
# [1296] Divide Array in Sets of K Consecutive Numbers
#
# https://leetcode.com/problems/divide-array-in-sets-of-k-consecutive-numbers/description/
#
# algorithms
# Medium (59.42%)
# Likes:    2008
# Dislikes: 119
# Total Accepted:    135K
# Total Submissions: 227K
# Testcase Example:  "[1,2,3,3,4,4,5,6]"
#
# Given an array of integers nums and a positive integer k, check whether it is
# possible to divide this array into sets of k consecutive numbers.
#
# Return true if it is possible. Otherwise, return false.
#
# Example 1:
#
# Input: nums = [1,2,3,3,4,4,5,6], k = 4
# Output: true
# Explanation: Array can be divided into [1,2,3,4] and [3,4,5,6].
#
# Example 2:
#
# Input: nums = [3,2,1,2,3,4,3,4,5,9,10,11], k = 3
# Output: true
# Explanation: Array can be divided into [1,2,3] , [2,3,4] , [3,4,5] and
# [9,10,11].
#
# Example 3:
#
# Input: nums = [1,2,3,4], k = 3
# Output: false
# Explanation: Each array should be divided in subarrays of size 3.
#
# Constraints:
#
# 1 <= k <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# Note: This question is the same as 846:
# https://leetcode.com/problems/hand-of-straights/
#

# @lc code=start

from typing import List
from collections import Counter


class Solution:
    def isPossibleDivide(self, nums: List[int], k: int) -> bool:
        """
        Interview explanation:
        Same as Hand of Straights: partition into groups of k consecutive.
        Count frequencies; repeatedly take the smallest remaining as start of
        a group of k.

        Algorithm:
        - Counter; while counts: start=min key; for x in start..start+k-1:
          decrement; fail if missing. Return True.

        Complexity: O(n log n) with sorted keys each time, or O(n log n) sort once.
        """
        if len(nums) % k:
            return False
        cnt = Counter(nums)
        for start in sorted(cnt):
            need = cnt[start]
            if need == 0:
                continue
            for x in range(start, start + k):
                if cnt[x] < need:
                    return False
                cnt[x] -= need
        return True

    def isPossibleDivide_heap(self, nums: List[int], k: int) -> bool:
        """
        Interview explanation:
        Alternate: heap of unique numbers; pop starts and consume k consecutive.

        Algorithm:
        - Counter + min-heap of keys; while heap: start=heappop; consume.

        Complexity: O(n log n).
        """
        import heapq

        if len(nums) % k:
            return False
        cnt = Counter(nums)
        heap = list(cnt.keys())
        heapq.heapify(heap)
        while heap:
            while heap and cnt[heap[0]] == 0:
                heapq.heappop(heap)
            if not heap:
                break
            start = heap[0]
            for x in range(start, start + k):
                if cnt[x] == 0:
                    return False
                cnt[x] -= 1
        return True
# @lc code=end
