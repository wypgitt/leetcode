#
# @lc app=leetcode id=3254 lang=python3
#
# [3254] Find the Power of K-Size Subarrays I
#
# https://leetcode.com/problems/find-the-power-of-k-size-subarrays-i/description/
#
# algorithms
# Medium (62.10%)
# Likes:    683
# Dislikes: 58
# Total Accepted:    157K
# Total Submissions: 252.8K
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
# 1 <= n == nums.length <= 500
#
# 1 <= nums[i] <= 10^5
#
# 1 <= k <= n
#

# @lc code=start
from typing import List


class Solution:
    def resultsArray(self, nums: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        Power is the max iff the window is consecutive ascending by +1; else -1.
        Track the length of the current consecutive-increasing streak.

        Algorithm:
        - Scan left to right; extend streak when nums[i]==nums[i-1]+1.
        - Window ending at i is valid when streak >= k; value is nums[i].

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
