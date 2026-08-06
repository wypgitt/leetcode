#
# @lc app=leetcode id=3255 lang=python3
#
# [3255] Find the Power of K-Size Subarrays II
#
# https://leetcode.com/problems/find-the-power-of-k-size-subarrays-ii/description/
#
# algorithms
# Medium (31.96%)
# Likes:    167
# Dislikes: 12
# Total Accepted:    36.2K
# Total Submissions: 113.4K
# Testcase Example:  "[1,2,3,4,3,2,5]\n3"
#
#
# You are given an array of integers nums of length n and a positive
# integer k.
#
# The power of an array is defined as:
#
# Its maximum element if all of its elements are consecutive and sorted in
# ascending order.
#
# -1 otherwise.
#
# You need to find the power of all subarrays of nums of size k.
#
# Return an integer array results of size n - k + 1, where results[i] is
# the power of nums[i..(i + k - 1)].
#
# Example 1:
#
# Input: nums = [1,2,3,4,3,2,5], k = 3
#
# Output: [3,4,-1,-1,-1]
#
# Explanation:
#
# There are 5 subarrays of nums of size 3:
#
# [1, 2, 3] with the maximum element 3.
#
# [2, 3, 4] with the maximum element 4.
#
# [3, 4, 3] whose elements are not consecutive.
#
# [4, 3, 2] whose elements are not sorted.
#
# [3, 2, 5] whose elements are not consecutive.
#
# Example 2:
#
# Input: nums = [2,2,2,2,2], k = 4
#
# Output: [-1,-1]
#
# Example 3:
#
# Input: nums = [3,2,3,2,3,2], k = 2
#
# Output: [-1,3,-1,3,-1]
#
# Constraints:
#
# 1 <= n == nums.length <= 10^5
#
# 1 <= nums[i] <= 10^6
#
# 1 <= k <= n
#

# @lc code=start
from typing import List


class Solution:
    def resultsArray(self, nums: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        Same as Power of K-Size Subarrays I with n up to 1e5: one linear pass
        tracking consecutive +1 streak length is enough.

        Algorithm:
        - Maintain streak of nums[i] == nums[i-1] + 1.
        - If streak >= k at index i, results[i-k+1] = nums[i], else -1.

        Complexity: O(n) time, O(1) extra space.
        """
        n = len(nums)
        ans = [-1] * (n - k + 1)
        streak = 0
        for i, x in enumerate(nums):
            if i > 0 and x == nums[i - 1] + 1:
                streak += 1
            else:
                streak = 1
            if streak >= k:
                ans[i - k + 1] = x
        return ans
# @lc code=end
