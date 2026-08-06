#
# @lc app=leetcode id=3511 lang=python3
#
# [3511] Make a Positive Array
#
# https://leetcode.com/problems/make-a-positive-array/description/
#
# algorithms
# Medium (36.63%)
# Likes:    8
# Dislikes: 7
# Total Accepted:    852
# Total Submissions: 2.3K
# Testcase Example:  "[-10,15,-12]"
#
#
# You are given an array nums. An array is considered positive if the sum
# of all numbers in each subarray with more than two elements is positive.
#
# You can perform the following operation any number of times:
#
# Replace one element in nums with any integer between -10^18 and 10^18.
#
# Find the minimum number of operations needed to make nums positive.
#
# Example 1:
#
# Input: nums = [-10,15,-12]
#
# Output: 1
#
# Explanation:
#
# The only subarray with more than 2 elements is the array itself. The sum
# of all elements is (-10) + 15 + (-12) = -7. By replacing nums[0] with 0,
# the new sum becomes 0 + 15 + (-12) = 3. Thus, the array is now positive.
#
# Example 2:
#
# Input: nums = [-1,-2,3,-1,2,6]
#
# Output: 1
#
# Explanation:
#
# The only subarrays with more than 2 elements and a non-positive sum are:
#
#                         Subarray Indices
#                         Subarray
#                         Sum
#                         Subarray After Replacement (Set nums[1] = 1)
#                         New Sum
#
#                         nums[0...2]
#                         [-1, -2, 3]
#                         0
#                         [-1, 1, 3]
#                         3
#
#                         nums[0...3]
#                         [-1, -2, 3, -1]
#                         -1
#                         [-1, 1, 3, -1]
#                         2
#
#                         nums[1...3]
#                         [-2, 3, -1]
#                         0
#                         [1, 3, -1]
#                         3
#
# Thus, nums is positive after one operation.
#
# Example 3:
#
# Input: nums = [1,2,3]
#
# Output: 0
#
# Explanation:
#
# The array is already positive, so no operations are needed.
#
# Constraints:
#
# 3 <= nums.length <= 10^5
#
# -10^9 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def makeArrayPositive(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Every subarray of length >= 3 must have positive sum. Greedily, when the
        minimum sum among subarrays ending at i becomes non-positive, replace
        nums[i] with a huge positive value (one operation).

        Algorithm:
        - Track minSum = min sum of length>=3 subarrays ending at current index.
        - minSum = min(minSum + a[i], a[i-2]+a[i-1]+a[i]); if <= 0, set a[i]=1e18.

        Complexity: O(n) time, O(1) extra space.
        """
        MAX = 10**18
        a = list(nums)
        ans = 0
        min_sum = a[0] + a[1]
        for i in range(2, len(a)):
            min_sum = min(min_sum + a[i], a[i - 2] + a[i - 1] + a[i])
            if min_sum <= 0:
                a[i] = MAX
                min_sum = MAX
                ans += 1
        return ans
# @lc code=end
