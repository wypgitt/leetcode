#
# @lc app=leetcode id=78 lang=python3
#
# [78] Subsets
#
# https://leetcode.com/problems/subsets/description/
#
# algorithms
# Medium (82.30%)
# Likes:    19262
# Dislikes: 341
# Total Accepted:    3M
# Total Submissions: 3.7M
# Testcase Example:  '[1,2,3]'
#
# Given an integer array nums of unique elements, return all possible subsets
# (the power set).
# 
# The solution set must not contain duplicate subsets. Return the solution in
# any order.
# 
# 
# Example 1:
# 
# 
# Input: nums = [1,2,3]
# Output: [[],[1],[2],[1,2],[3],[1,3],[2,3],[1,2,3]]
# 
# 
# Example 2:
# 
# 
# Input: nums = [0]
# Output: [[],[0]]
# 
# 
# 
# Constraints:
# 
# 
# 1 <= nums.length <= 10
# -10 <= nums[i] <= 10
# All the numbers of nums are unique.
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def subsets(self, nums: List[int]) -> List[List[int]]:
        """
        Interview explanation:
        For each number there are two choices: exclude it or include it. An
        iterative approach starts with the empty subset and, for each number,
        appends that number to every subset built so far.

        Edge cases and tests:
        - Empty input would produce [[]].
        - One element produces [[], [x]].
        - Distinct values mean no duplicate subsets.

        Complexity: O(2^n * n) time including copies, O(2^n * n) output space.
        """
        ans = [[]]
        for num in nums:
            ans += [subset + [num] for subset in ans]
        return ans
# @lc code=end


