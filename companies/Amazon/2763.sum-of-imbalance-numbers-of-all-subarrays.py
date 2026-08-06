#
# @lc app=leetcode id=2763 lang=python3
#
# [2763] Sum of Imbalance Numbers of All Subarrays
#
# https://leetcode.com/problems/sum-of-imbalance-numbers-of-all-subarrays/description/
#
# algorithms
# Hard (43.78%)
# Likes:    329
# Dislikes: 9
# Total Accepted:    10.2K
# Total Submissions: 23.3K
# Testcase Example:  "[2,3,1,4]"
#
# The imbalance number of a 0-indexed integer array arr of length n is defined
# as the number of indices in sarr = sorted(arr) such that:
#
#
# 0 <= i < n - 1, and
#
#
# sarr[i+1] - sarr[i] > 1
#
# Here, sorted(arr) is the function that returns the sorted version of arr.
#
# Given a 0-indexed integer array nums, return the sum of imbalance numbers of
# all its subarrays.
#
# A subarray is a contiguous non-empty sequence of elements within an array.
#
#
#
# Example 1:
#
# Input: nums = [2,3,1,4]
# Output: 3
# Explanation: There are 3 subarrays with non-zero imbalance numbers:
# - Subarray [3, 1] with an imbalance number of 1.
# - Subarray [3, 1, 4] with an imbalance number of 1.
# - Subarray [1, 4] with an imbalance number of 1.
# The imbalance number of all other subarrays is 0. Hence, the sum of imbalance
# numbers of all the subarrays of nums is 3.
#
# Example 2:
#
# Input: nums = [1,3,3,3,5]
# Output: 8
# Explanation: There are 7 subarrays with non-zero imbalance numbers:
# - Subarray [1, 3] with an imbalance number of 1.
# - Subarray [1, 3, 3] with an imbalance number of 1.
# - Subarray [1, 3, 3, 3] with an imbalance number of 1.
# - Subarray [1, 3, 3, 3, 5] with an imbalance number of 2.
# - Subarray [3, 3, 3, 5] with an imbalance number of 1.
# - Subarray [3, 3, 5] with an imbalance number of 1.
# - Subarray [3, 5] with an imbalance number of 1.
# The imbalance number of all other subarrays is 0. Hence, the sum of imbalance
# numbers of all the subarrays of nums is 8.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 1000
#
#
# 1 <= nums[i] <= nums.length
#

# @lc code=start
from typing import List


class Solution:
    def sumImbalanceNumbers(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Imbalance of an array = gaps in its sorted unique values where consecutive
        distinct values differ by > 1. Sum imbalance over all subarrays.

        Algorithm:
        - Contribution: for each index i, count subarrays where nums[i] creates a
          gap above it (nearest nums[i]/nums[i]+1 on left, nums[i]+1 on right).
        - Subtract n(n+1)/2 (each subarray's max was overcounted as a gap).

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        left = [0] * n
        right = [0] * n
        last = [-1] * (n + 2)
        for i, x in enumerate(nums):
            left[i] = max(last[x], last[x + 1])
            last[x] = i
        last = [n] * (n + 2)
        for i in range(n - 1, -1, -1):
            right[i] = last[nums[i] + 1]
            last[nums[i]] = i
        return sum((i - left[i]) * (right[i] - i) for i in range(n)) - n * (n + 1) // 2

    def sumImbalanceNumbers_brute(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate O(n^2): extend subarrays while maintaining distinct set and
        incremental gap count.

        Algorithm:
        - For each left endpoint, grow right; on new distinct value, update gaps
          via neighbors x-1 and x+1 in the set.

        Complexity: O(n^2) time, O(n) space.
        """
        n = len(nums)
        ans = 0
        for i in range(n):
            seen = {nums[i]}
            gaps = 0
            for j in range(i + 1, n):
                x = nums[j]
                if x not in seen:
                    gaps += 1
                    if x - 1 in seen:
                        gaps -= 1
                    if x + 1 in seen:
                        gaps -= 1
                    seen.add(x)
                ans += gaps
        return ans
# @lc code=end
