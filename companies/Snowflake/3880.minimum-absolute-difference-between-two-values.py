#
# @lc app=leetcode id=3880 lang=python3
#
# [3880] Minimum Absolute Difference Between Two Values
#
# https://leetcode.com/problems/minimum-absolute-difference-between-two-values/description/
#
# algorithms
# Easy (66.92%)
# Likes:    36
# Dislikes: 0
# Total Accepted:    42.2K
# Total Submissions: 63.1K
# Testcase Example:  "[1,0,0,2,0,1]"
#
#
# You are given an integer array nums consisting only of 0, 1, and 2.
#
# A pair of indices (i, j) is called valid if nums[i] == 1 and nums[j] ==
# 2.
#
# Return the minimum absolute difference between i and j among all valid
# pairs. If no valid pair exists, return -1.
#
# The absolute difference between indices i and j is defined as abs(i -
# j).
#
# Example 1:
#
# Input: nums = [1,0,0,2,0,1]
#
# Output: 2
#
# Explanation:
#
# The valid pairs are:
#
# (0, 3) which has absolute difference of abs(0 - 3) = 3.
#
# (5, 3) which has absolute difference of abs(5 - 3) = 2.
#
# Thus, the answer is 2.
#
# Example 2:
#
# Input: nums = [1,0,1,0]
#
# Output: -1
#
# Explanation:
#
# There are no valid pairs in the array, thus the answer is -1.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 0 <= nums[i] <= 2
#

# @lc code=start
class Solution:
    def minAbsoluteDifference(self, nums: list[int]) -> int:
        """
        Interview explanation:
        Minimize |i-j| over pairs with nums[i]==1 and nums[j]==2.

        Algorithm:
        - Track last seen indices of 1 and 2 while scanning.
        - Update answer whenever the other value is seen.

        Complexity: O(n) time, O(1) space.
        """
        ans = float("inf")
        last1 = last2 = -1
        for i, x in enumerate(nums):
            if x == 1:
                last1 = i
                if last2 != -1:
                    ans = min(ans, abs(i - last2))
            elif x == 2:
                last2 = i
                if last1 != -1:
                    ans = min(ans, abs(i - last1))
        return -1 if ans == float("inf") else ans
# @lc code=end
