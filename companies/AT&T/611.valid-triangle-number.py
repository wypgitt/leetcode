#
# @lc app=leetcode id=611 lang=python3
#
# [611] Valid Triangle Number
#
# https://leetcode.com/problems/valid-triangle-number/description/
#
# algorithms
# Medium (56.86%)
# Likes:    4449
# Dislikes: 262
# Total Accepted:    367.3K
# Total Submissions: 645.9K
# Testcase Example:  '[2,2,3,4]'
#
# Given an integer array nums, return the number of triplets chosen from the
# array that can make triangles if we take them as side lengths of a
# triangle.
# 
# 
# Example 1:
# 
# 
# Input: nums = [2,2,3,4]
# Output: 3
# Explanation: Valid combinations are: 
# 2,3,4 (using the first 2)
# 2,3,4 (using the second 2)
# 2,2,3
# 
# 
# Example 2:
# 
# 
# Input: nums = [4,2,3,4]
# Output: 4
# 
# 
# 
# Constraints:
# 
# 
# 1 <= nums.length <= 1000
# 0 <= nums[i] <= 1000
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def triangleNumber(self, nums: List[int]) -> int:
        nums.sort()
        ans = 0
        for k in range(len(nums) - 1, 1, -1):
            i, j = 0, k - 1
            while i < j:
                if nums[i] + nums[j] > nums[k]:
                    ans += j - i
                    j -= 1
                else:
                    i += 1
        return ans
# @lc code=end

"""
Interview explanation:
After sorting, choose nums[k] as the largest side. The triangle condition reduces to nums[i] + nums[j] > nums[k]. With two pointers, if i+j works, then every index from i through j-1 paired with j also works because the array is sorted.

Data structure: sorted array plus two pointers.

Edge cases: zeros naturally fail the strict inequality. Arrays shorter than 3 return 0.

Complexity: sorting costs O(n log n), the nested two-pointer scans cost O(n^2), so total O(n^2). Extra space is O(1) besides sorting.
"""
