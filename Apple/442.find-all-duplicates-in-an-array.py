#
# @lc app=leetcode id=442 lang=python3
#
# [442] Find All Duplicates in an Array
#
# https://leetcode.com/problems/find-all-duplicates-in-an-array/description/
#
# algorithms
# Medium (77.08%)
# Likes:    11238
# Dislikes: 449
# Total Accepted:    1.1M
# Total Submissions: 1.4M
# Testcase Example:  "[4,3,2,7,8,2,3,1]"
#
# Given an integer array nums of length n where all the integers of nums are in
# the range [1, n] and each integer appears at most twice, return an array of
# all the integers that appears twice.
#
# You must write an algorithm that runs in O(n) time and uses only constant
# auxiliary space, excluding the space needed to store the output
#
# Example 1:
#
# Input: nums = [4,3,2,7,8,2,3,1]
# Output: [2,3]
#
# Example 2:
#
# Input: nums = [1,1,2]
# Output: [1]
#
# Example 3:
#
# Input: nums = [1]
# Output: []
#
# Constraints:
#
# n == nums.length
#
# 1 <= n <= 10^5
#
# 1 <= nums[i] <= n
#
# Each element in nums appears once or twice.
#

# @lc code=start

from typing import List


class Solution:
    def findDuplicates(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Index-mark: values are in 1..n. Negate nums[abs(x)-1] when seeing x;
        if already negative, x is a duplicate. O(1) extra space.

        Algorithm:
        - For each x: i=abs(x)-1; if nums[i]<0: x is dup; else nums[i]=-nums[i].

        Complexity: O(n) time, O(1) extra space (output excluded).
        """
        ans = []
        for x in nums:
            i = abs(x) - 1
            if nums[i] < 0:
                ans.append(abs(x))
            else:
                nums[i] = -nums[i]
        return ans
# @lc code=end
