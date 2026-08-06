#
# @lc app=leetcode id=90 lang=python3
#
# [90] Subsets II
#
# https://leetcode.com/problems/subsets-ii/description/
#
# algorithms
# Medium (61.24%)
# Likes:    10970
# Dislikes: 418
# Total Accepted:    1.5M
# Total Submissions: 2.4M
# Testcase Example:  '[1,2,2]'
#
# Given an integer array nums that may contain duplicates, return all possible
# subsets (the power set).
# 
# The solution set must not contain duplicate subsets. Return the solution in
# any order.
# 
# 
# Example 1:
# Input: nums = [1,2,2]
# Output: [[],[1],[1,2],[1,2,2],[2],[2,2]]
# Example 2:
# Input: nums = [0]
# Output: [[],[0]]
# 
# 
# Constraints:
# 
# 
# 1 <= nums.length <= 10
# -10 <= nums[i] <= 10
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def subsetsWithDup(self, nums: List[int]) -> List[List[int]]:
        """
        Interview explanation:
        Sort the array so duplicates are adjacent. During backtracking, skip a
        duplicate value if the previous equal value was not chosen at this same
        recursion depth; otherwise the same subset would be generated again.

        Edge cases and tests:
        - [1,2,2] produces six subsets, not eight.
        - All duplicates produce n+1 subsets by count.
        - Empty subset is always included.

        Complexity: O(U * n) time where U is the number of unique subsets, O(n)
        recursion space excluding output.
        """
        nums.sort()
        ans = []
        path = []

        def dfs(start: int) -> None:
            ans.append(path.copy())
            for i in range(start, len(nums)):
                if i > start and nums[i] == nums[i - 1]:
                    continue
                path.append(nums[i])
                dfs(i + 1)
                path.pop()

        dfs(0)
        return ans
# @lc code=end


