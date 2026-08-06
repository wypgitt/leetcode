#
# @lc app=leetcode id=1099 lang=python3
#
# [1099] Two Sum Less Than K
#
# https://leetcode.com/problems/two-sum-less-than-k/description/
#
# algorithms
# Easy (62.16%)
# Likes:    1176
# Dislikes: 135
# Total Accepted:    150.1K
# Total Submissions: 241.5K
# Testcase Example:  "[34,23,1,24,75,33,54,8]\n60"
#
#
# Given an array nums of integers and integer k, return the maximum sum
# such that there exists i < j with nums[i] + nums[j] = sum and sum < k.
# If no i, j exist satisfying this equation, return -1.
#
# Example 1:
#
# Input: nums = [34,23,1,24,75,33,54,8], k = 60
# Output: 58
# Explanation: We can use 34 and 24 to sum 58 which is less than 60.
#
# Example 2:
#
# Input: nums = [10,20,30], k = 15
# Output: -1
# Explanation: In this case it is not possible to get a pair sum less that
# 15.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 1 <= nums[i] <= 1000
#
# 1 <= k <= 2000
#
# @lc code=start
from typing import List


class Solution:
    def twoSumLessThanK(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Premium. Maximum A[i]+A[j] (i<j) strictly less than k, or -1.
        Sort then two pointers from both ends.

        Algorithm (sort + two pointers):
        - Sort nums; lo=0, hi=n-1; best=-1.
        - If sum < k: best=max(best,sum); lo++. Else hi--.

        Complexity: O(n log n) time, O(n) or O(1) depending on sort.
        """
        nums = sorted(nums)
        lo, hi = 0, len(nums) - 1
        best = -1
        while lo < hi:
            s = nums[lo] + nums[hi]
            if s < k:
                best = max(best, s)
                lo += 1
            else:
                hi -= 1
        return best
# @lc code=end
