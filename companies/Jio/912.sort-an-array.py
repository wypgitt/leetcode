#
# @lc app=leetcode id=912 lang=python3
#
# [912] Sort an Array
#
# https://leetcode.com/problems/sort-an-array/description/
#
# algorithms
# Medium (55.87%)
# Likes:    7330
# Dislikes: 849
# Total Accepted:    1.2M
# Total Submissions: 2.1M
# Testcase Example:  "[5,2,3,1]"
#
# Given an array of integers nums, sort the array in ascending order and return
# it.
#
# You must solve the problem without using any built-in functions in O(nlog(n))
# time complexity and with the smallest space complexity possible.
#
# Example 1:
#
# Input: nums = [5,2,3,1]
# Output: [1,2,3,5]
# Explanation: After sorting the array, the positions of some numbers are not
# changed (for example, 2 and 3), while the positions of other numbers are
# changed (for example, 1 and 5).
#
# Example 2:
#
# Input: nums = [5,1,1,2,0,0]
# Output: [0,0,1,1,2,5]
# Explanation: Note that the values of nums are not necessarily unique.
#
# Constraints:
#
# 1 <= nums.length <= 5 * 10^4
#
# -5 * 10^4 <= nums[i] <= 5 * 10^4
#

# @lc code=start
import heapq
from typing import List


class Solution:
    def sortArray(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Sort without relying on library sort for interview — classic mergesort
        (stable, guaranteed O(n log n)).

        Algorithm (merge sort):
        - Recursively sort halves; merge two sorted arrays.

        Complexity: O(n log n) time, O(n) space.
        """
        def merge_sort(arr: List[int]) -> List[int]:
            if len(arr) <= 1:
                return arr
            mid = len(arr) // 2
            left = merge_sort(arr[:mid])
            right = merge_sort(arr[mid:])
            return merge(left, right)

        def merge(a: List[int], b: List[int]) -> List[int]:
            i = j = 0
            out: List[int] = []
            while i < len(a) and j < len(b):
                if a[i] <= b[j]:
                    out.append(a[i])
                    i += 1
                else:
                    out.append(b[j])
                    j += 1
            out.extend(a[i:])
            out.extend(b[j:])
            return out

        return merge_sort(nums)

    def sortArray_heap(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate: heapsort via heapq (or build binary heap in-place).

        Algorithm:
        - heapify nums; repeatedly heappop into result.

        Complexity: O(n log n) time, O(n) space here.
        """
        heapq.heapify(nums)
        return [heapq.heappop(nums) for _ in range(len(nums))]

    def sortArray_quick(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate classic: quicksort with Lomuto/Hoare partition (avg O(n log n)).

        Algorithm:
        - Pick pivot; partition <pivot / >=pivot; recurse.

        Complexity: O(n log n) avg, O(n^2) worst; O(log n) stack.
        """
        def quicksort(lo: int, hi: int) -> None:
            if lo >= hi:
                return
            pivot = nums[(lo + hi) // 2]
            i, j = lo, hi
            while i <= j:
                while nums[i] < pivot:
                    i += 1
                while nums[j] > pivot:
                    j -= 1
                if i <= j:
                    nums[i], nums[j] = nums[j], nums[i]
                    i += 1
                    j -= 1
            quicksort(lo, j)
            quicksort(i, hi)

        quicksort(0, len(nums) - 1)
        return nums
# @lc code=end

