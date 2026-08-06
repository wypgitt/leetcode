#
# @lc app=leetcode id=565 lang=python3
#
# [565] Array Nesting
#
# https://leetcode.com/problems/array-nesting/description/
#
# algorithms
# Medium (56.63%)
# Likes:    2282
# Dislikes: 159
# Total Accepted:    149.6K
# Total Submissions: 264.1K
# Testcase Example:  '[5,4,0,3,1,6,2]'
#
# You are given an integer array nums of length n where nums is a permutation
# of the numbers in the range [0, n - 1].
# 
# You should build a set s[k] = {nums[k], nums[nums[k]], nums[nums[nums[k]]],
# ... } subjected to the following rule:
# 
# 
# The first element in s[k] starts with the selection of the element nums[k] of
# index = k.
# The next element in s[k] should be nums[nums[k]], and then
# nums[nums[nums[k]]], and so on.
# We stop adding right before a duplicate element occurs in s[k].
# 
# 
# Return the longest length of a set s[k].
# 
# 
# Example 1:
# 
# 
# Input: nums = [5,4,0,3,1,6,2]
# Output: 4
# Explanation: 
# nums[0] = 5, nums[1] = 4, nums[2] = 0, nums[3] = 3, nums[4] = 1, nums[5] = 6,
# nums[6] = 2.
# One of the longest sets s[k]:
# s[0] = {nums[0], nums[5], nums[6], nums[2]} = {5, 6, 2, 0}
# 
# 
# Example 2:
# 
# 
# Input: nums = [0,1,2]
# Output: 1
# 
# 
# 
# Constraints:
# 
# 
# 1 <= nums.length <= 10^5
# 0 <= nums[i] < nums.length
# All the values of nums are unique.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def arrayNesting(self, nums: List[int]) -> int:
        best = 0
        for i in range(len(nums)):
            if nums[i] == -1:
                continue
            count = 0
            j = i
            while nums[j] != -1:
                nxt = nums[j]
                nums[j] = -1
                j = nxt
                count += 1
            best = max(best, count)
        return best
# @lc code=end

"""
Interview explanation:
Because nums is a permutation of 0..n-1, following nums[i] eventually forms a cycle. Each index belongs to exactly one such component, so mark indices as visited while walking and record the largest cycle length.

Data structure: the array itself is used as the visited marker by writing -1, which is outside the valid value range.

Edge cases: already visited starts are skipped. A one-element cycle counts as length 1.

Complexity: every index is visited once, so O(n) time and O(1) extra space. The input array is modified; use a boolean visited array if mutation is not allowed.
"""
