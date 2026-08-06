#
# @lc app=leetcode id=324 lang=python3
#
# [324] Wiggle Sort II
#
# https://leetcode.com/problems/wiggle-sort-ii/description/
#
# algorithms
# Medium (37.94%)
# Likes:    3273
# Dislikes: 983
# Total Accepted:    214K
# Total Submissions: 564K
# Testcase Example:  "[1,5,1,1,6,4]"
#
# Given an integer array nums, reorder it such that nums[0] < nums[1] > nums[2]
# < nums[3]....
#
# You may assume the input array always has a valid answer.
#
# Example 1:
#
# Input: nums = [1,5,1,1,6,4]
# Output: [1,6,1,5,1,4]
# Explanation: [1,4,1,5,1,6] is also accepted.
#
# Example 2:
#
# Input: nums = [1,3,2,2,3,1]
# Output: [2,3,1,3,1,2]
#
# Constraints:
#
# 1 <= nums.length <= 5 * 10^4
#
# 0 <= nums[i] <= 5000
#
# It is guaranteed that there will be an answer for the given input nums.
#
# Follow Up: Can you do it in O(n) time and/or in-place with O(1) extra space?
#

# @lc code=start
from typing import List


class Solution:
    def wiggleSort(self, nums: List[int]) -> None:
        """
        Interview explanation:
        Sort then place smaller half on even virtual indices and larger half
        on odd ones via index mapping (n|1) so neighbors come from opposite
        halves — guarantees nums[0] < nums[1] > nums[2] < ...

        Algorithm:
        - Sort a copy ascending.
        - Virtual index: (1 + 2*i) % (n|1) maps to wiggle positions.
        - Fill from largest to smallest into virtual order (or mid-split place).

        Complexity: O(n log n) time, O(n) space.
        Do not return anything, modify nums in-place instead.
        """
        n = len(nums)
        arr = sorted(nums)
        mid = (n + 1) // 2
        small = arr[:mid][::-1]
        large = arr[mid:][::-1]
        nums[::2] = small
        nums[1::2] = large

    def wiggleSort_virtual(self, nums: List[int]) -> None:
        """
        Interview explanation:
        Alternate classic: three-way partition around median then place via
        virtual index (1+2*i)%(n|1) for O(n) average with quickselect.

        Algorithm:
        - Find median; Dutch-flag partition into < / = / > median on virtual idxs.
        - Mapping puts large values on odd slots and small on even.

        Complexity: O(n) average time, O(1) extra space (excluding select).
        """
        n = len(nums)
        if n < 2:
            return

        def nth_element(k: int) -> int:
            a = nums[:]
            lo, hi = 0, n - 1
            while True:
                pivot = a[(lo + hi) // 2]
                i, j = lo, hi
                while i <= j:
                    while a[i] < pivot:
                        i += 1
                    while a[j] > pivot:
                        j -= 1
                    if i <= j:
                        a[i], a[j] = a[j], a[i]
                        i += 1
                        j -= 1
                if k <= j:
                    hi = j
                elif k >= i:
                    lo = i
                else:
                    return a[k]

        mid = nth_element(n // 2)
        # Virtual index access
        def A(i: int) -> int:
            return (1 + 2 * i) % (n | 1)

        i = j = 0
        k = n - 1
        while j <= k:
            if nums[A(j)] > mid:
                nums[A(i)], nums[A(j)] = nums[A(j)], nums[A(i)]
                i += 1
                j += 1
            elif nums[A(j)] < mid:
                nums[A(j)], nums[A(k)] = nums[A(k)], nums[A(j)]
                k -= 1
            else:
                j += 1
# @lc code=end
