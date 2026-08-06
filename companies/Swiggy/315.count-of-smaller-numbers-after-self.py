#
# @lc app=leetcode id=315 lang=python3
#
# [315] Count of Smaller Numbers After Self
#
# https://leetcode.com/problems/count-of-smaller-numbers-after-self/description/
#
# algorithms
# Hard (43.89%)
# Likes:    9325
# Dislikes: 256
# Total Accepted:    403K
# Total Submissions: 919K
# Testcase Example:  "[5,2,6,1]"
#
# Given an integer array nums, return an integer array counts where counts[i]
# is the number of smaller elements to the right of nums[i].
#
# Example 1:
#
# Input: nums = [5,2,6,1]
# Output: [2,1,1,0]
# Explanation:
# To the right of 5 there are 2 smaller elements (2 and 1).
# To the right of 2 there is only 1 smaller element (1).
# To the right of 6 there is 1 smaller element (1).
# To the right of 1 there is 0 smaller element.
#
# Example 2:
#
# Input: nums = [-1]
# Output: [0]
#
# Example 3:
#
# Input: nums = [-1,-1]
# Output: [0,0]
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -10^4 <= nums[i] <= 10^4
#

# @lc code=start
from typing import List


class Solution:
    def countSmaller(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        For each index i, count j > i with nums[j] < nums[i]. Merge-sort while
        counting how many right-half elements are smaller when taking from left.

        Algorithm (merge sort — primary):
        - Sort indices by value; when merging, if left[i] value > right[j],
          those remaining left indices each gain (right_ptr progress) counts...
          Standard: when taking from right half, increment a running "right
          taken" count; when taking from left, add that count to ans[left_idx].

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(nums)
        ans = [0] * n
        idx = list(range(n))

        def merge_sort(arr: List[int]) -> List[int]:
            if len(arr) <= 1:
                return arr
            mid = len(arr) // 2
            left = merge_sort(arr[:mid])
            right = merge_sort(arr[mid:])
            merged = []
            i = j = 0
            while i < len(left) or j < len(right):
                if j == len(right) or (
                    i < len(left) and nums[left[i]] <= nums[right[j]]
                ):
                    ans[left[i]] += j
                    merged.append(left[i])
                    i += 1
                else:
                    merged.append(right[j])
                    j += 1
            return merged

        merge_sort(idx)
        return ans

    def countSmallerBIT(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate: Fenwick tree on ranks. Scan right-to-left; query how many
        already-seen values are smaller, then update current rank.

        Complexity: O(n log n) time, O(n) space.
        """
        sorted_unique = sorted(set(nums))
        rank = {v: i + 1 for i, v in enumerate(sorted_unique)}
        m = len(sorted_unique)
        bit = [0] * (m + 1)

        def add(i: int, delta: int) -> None:
            while i <= m:
                bit[i] += delta
                i += i & -i

        def prefix(i: int) -> int:
            s = 0
            while i > 0:
                s += bit[i]
                i -= i & -i
            return s

        ans = [0] * len(nums)
        for i in range(len(nums) - 1, -1, -1):
            r = rank[nums[i]]
            ans[i] = prefix(r - 1)
            add(r, 1)
        return ans
# @lc code=end

