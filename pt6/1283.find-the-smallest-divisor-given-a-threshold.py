#
# @lc app=leetcode id=1283 lang=python3
#
# [1283] Find the Smallest Divisor Given a Threshold
#
# https://leetcode.com/problems/find-the-smallest-divisor-given-a-threshold/description/
#
# algorithms
# Medium (65.84%)
# Likes:    3606
# Dislikes: 230
# Total Accepted:    454.9K
# Total Submissions: 690.6K
# Testcase Example:  '[1,2,5,9]\n6'
#
# Given an array of integers nums and an integer threshold, we will choose a
# positive integer divisor, divide all the array by it, and sum the division's
# result. Find the smallest divisor such that the result mentioned above is
# less than or equal to threshold.
# 
# Each result of the division is rounded to the nearest integer greater than or
# equal to that element. (For example: 7/3 = 3 and 10/2 = 5).
# 
# The test cases are generated so that there will be an answer.
# 
# 
# Example 1:
# 
# 
# Input: nums = [1,2,5,9], threshold = 6
# Output: 5
# Explanation: We can get a sum to 17 (1+2+5+9) if the divisor is 1. 
# If the divisor is 4 we can get a sum of 7 (1+1+2+3) and if the divisor is 5
# the sum will be 5 (1+1+1+2). 
# 
# 
# Example 2:
# 
# 
# Input: nums = [44,22,33,11,1], threshold = 5
# Output: 44
# 
# 
# 
# Constraints:
# 
# 
# 1 <= nums.length <= 5 * 10^4
# 1 <= nums[i] <= 10^6
# nums.length <= threshold <= 10^6
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def smallestDivisor(self, nums: List[int], threshold: int) -> int:
        def needed(divisor: int) -> int:
            total = 0
            for num in nums:
                total += (num + divisor - 1) // divisor
                if total > threshold:
                    break
            return total

        left, right = 1, max(nums)

        while left < right:
            mid = (left + right) // 2
            if needed(mid) <= threshold:
                right = mid
            else:
                left = mid + 1

        return left
# @lc code=end

# Explanation
# -----------
# For a fixed divisor d, the required sum is
# sum(ceil(num / d)). As d increases, this sum never increases. That monotonic
# predicate lets us binary search for the smallest divisor whose sum is within
# threshold.
#
# The helper uses integer ceiling division (num + d - 1) // d and can stop
# early once the threshold is exceeded.
#
# Edge cases: divisor 1 gives the largest possible sum; max(nums) is always a
# valid upper bound under the problem constraints; exact threshold matches are
# accepted while search continues left.
#
# Time complexity: O(n log max(nums)).
# Space complexity: O(1).
