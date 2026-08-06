#
# @lc app=leetcode id=2970 lang=python3
#
# [2970] Count the Number of Incremovable Subarrays I
#
# https://leetcode.com/problems/count-the-number-of-incremovable-subarrays-i/description/
#
# algorithms
# Easy (56.37%)
# Likes:    205
# Dislikes: 129
# Total Accepted:    31.2K
# Total Submissions: 55.4K
# Testcase Example:  "[1,2,3,4]"
#
#
# You are given a 0-indexed array of positive integers nums.
#
# A subarray of nums is called incremovable if nums becomes strictly
# increasing on removing the subarray. For example, the subarray [3, 4] is
# an incremovable subarray of [5, 3, 4, 6, 7] because removing this
# subarray changes the array [5, 3, 4, 6, 7] to [5, 6, 7] which is
# strictly increasing.
#
# Return the total number of incremovable subarrays of nums.
#
# Note that an empty array is considered strictly increasing.
#
# A subarray is a contiguous non-empty sequence of elements within an
# array.
#
# Example 1:
#
# Input: nums = [1,2,3,4]
# Output: 10
# Explanation: The 10 incremovable subarrays are: [1], [2], [3], [4],
# [1,2], [2,3], [3,4], [1,2,3], [2,3,4], and [1,2,3,4], because on
# removing any one of these subarrays nums becomes strictly increasing.
# Note that you cannot select an empty subarray.
#
# Example 2:
#
# Input: nums = [6,5,7,8]
# Output: 7
# Explanation: The 7 incremovable subarrays are: [5], [6], [5,7], [6,5],
# [5,7,8], [6,5,7] and [6,5,7,8].
# It can be shown that there are only 7 incremovable subarrays in nums.
#
# Example 3:
#
# Input: nums = [8,7,6,6]
# Output: 3
# Explanation: The 3 incremovable subarrays are: [8,7,6], [7,6,6], and
# [8,7,6,6]. Note that [8,7] is not an incremovable subarray because after
# removing [8,7] nums becomes [6,6], which is sorted in ascending order
# but not strictly increasing.
#
# Constraints:
#
# 1 <= nums.length <= 50
#
# 1 <= nums[i] <= 50
#

# @lc code=start
from typing import List


class Solution:
    def incremovableSubarrayCount(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Count non-empty subarrays whose removal leaves a strictly increasing sequence
        (empty remainder counts as increasing). n <= 50 → brute is fine.

        Algorithm:
        - For every [l,r], check that prefix [0..l) and suffix (r..n) are strictly
          increasing and nums[l-1] < nums[r+1] when both sides exist.

        Complexity: O(n^3) time, O(1) space.
        """
        n = len(nums)
        ans = 0
        for l in range(n):
            for r in range(l, n):
                ok = True
                prev = None
                for i in range(l):
                    if prev is not None and nums[i] <= prev:
                        ok = False
                        break
                    prev = nums[i]
                if not ok:
                    continue
                for i in range(r + 1, n):
                    if prev is not None and nums[i] <= prev:
                        ok = False
                        break
                    prev = nums[i]
                if ok:
                    ans += 1
        return ans

    def incremovableSubarrayCount_two_pointers(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate O(n): only a strictly-increasing prefix and suffix can remain.

        Algorithm:
        - Find max increasing prefix end i and suffix start j. Combine with two pointers
          (same as hard version 2972).

        Complexity: O(n) time, O(1) space.
        """
        n = len(nums)
        i = 0
        while i + 1 < n and nums[i] < nums[i + 1]:
            i += 1
        if i == n - 1:
            return n * (n + 1) // 2
        ans = i + 2
        j = n - 1
        while j and nums[j - 1] < nums[j]:
            j -= 1
        k = 0
        for j2 in range(j, n):
            while k <= i and nums[k] < nums[j2]:
                k += 1
            ans += k + 1
        return ans
# @lc code=end
