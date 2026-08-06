#
# @lc app=leetcode id=46 lang=python3
#
# [46] Permutations
#
# https://leetcode.com/problems/permutations/description/
#
# algorithms
# Medium (81.89%)
# Likes:    20903
# Dislikes: 385
# Total Accepted:    3.1M
# Total Submissions: 3.8M
# Testcase Example:  '[1,2,3]'
#
# Given an array nums of distinct integers, return all the possible
# permutations. You can return the answer in any order.
# 
# 
# Example 1:
# Input: nums = [1,2,3]
# Output: [[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]
# Example 2:
# Input: nums = [0,1]
# Output: [[0,1],[1,0]]
# Example 3:
# Input: nums = [1]
# Output: [[1]]
# 
# 
# Constraints:
# 
# 
# 1 <= nums.length <= 6
# -10 <= nums[i] <= 10
# All the integers of nums are unique.
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def permute(self, nums: List[int]) -> List[List[int]]:
        """
        Interview explanation:
        A permutation is built by choosing one unused number for each position.
        Backtracking with a used boolean array gives O(1) membership checks and
        keeps the path in the chosen order.

        Edge cases and tests:
        - Single element returns [[x]].
        - The output count is n!.
        - Input values are distinct by problem definition.

        Complexity: O(n! * n) time because each output copy has length n, and
        O(n) recursion/used space excluding output.
        """
        ans = []
        path = []
        used = [False] * len(nums)

        def dfs() -> None:
            if len(path) == len(nums):
                ans.append(path.copy())
                return
            for i, val in enumerate(nums):
                if used[i]:
                    continue
                used[i] = True
                path.append(val)
                dfs()
                path.pop()
                used[i] = False

        dfs()
        return ans
# @lc code=end


