#
# @lc app=leetcode id=2444 lang=python3
#
# [2444] Count Subarrays With Fixed Bounds
#
# https://leetcode.com/problems/count-subarrays-with-fixed-bounds/description/
#
# algorithms
# Hard (69.18%)
# Likes:    3804
# Dislikes: 97
# Total Accepted:    237.2K
# Total Submissions: 342.9K
# Testcase Example:  "[1,3,5,2,7,5]\n1\n5"
#
# You are given an integer array nums and two integers minK and maxK.
#
# A fixed-bound subarray of nums is a subarray that satisfies the following
# conditions:
#
#
# The minimum value in the subarray is equal to minK.
#
#
# The maximum value in the subarray is equal to maxK.
#
# Return the number of fixed-bound subarrays.
#
# A subarray is a contiguous part of an array.
#
#
#
# Example 1:
#
# Input: nums = [1,3,5,2,7,5], minK = 1, maxK = 5
# Output: 2
# Explanation: The fixed-bound subarrays are [1,3,5] and [1,3,5,2].
#
# Example 2:
#
# Input: nums = [1,1,1,1], minK = 1, maxK = 1
# Output: 10
# Explanation: Every subarray of nums is a fixed-bound subarray. There are 10
# possible subarrays.
#
#
#
# Constraints:
#
#
# 2 <= nums.length <= 10^5
#
#
# 1 <= nums[i], minK, maxK <= 10^6
#

# @lc code=start
from typing import List


class Solution:
    def countSubarrays(self, nums: List[int], minK: int, maxK: int) -> int:
        """
        Interview explanation:
        Count subarrays whose minimum is minK and maximum is maxK.

        Algorithm:
        - Track last minK, maxK, and out-of-[minK,maxK]; at r add
          max(0, min(lastMin,lastMax)-lastBad).

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        last_min = last_max = last_bad = -1
        for i, x in enumerate(nums):
            if x < minK or x > maxK:
                last_bad = i
            if x == minK:
                last_min = i
            if x == maxK:
                last_max = i
            ans += max(0, min(last_min, last_max) - last_bad)
        return ans
# @lc code=end
