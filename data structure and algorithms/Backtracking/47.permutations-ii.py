#
# @lc app=leetcode id=47 lang=python3
#
# [47] Permutations II
#
# https://leetcode.com/problems/permutations-ii/description/
#
# algorithms
# Medium (63.39%)
# Likes:    9168
# Dislikes: 163
# Total Accepted:    1.3M
# Total Submissions: 2M
# Testcase Example:  '[1,1,2]'
#
# Given a collection of numbers, nums, that might contain duplicates, return
# all possible unique permutations in any order.
# 
# 
# Example 1:
# 
# 
# Input: nums = [1,1,2]
# Output:
# [[1,1,2],
# ⁠[1,2,1],
# ⁠[2,1,1]]
# 
# 
# Example 2:
# 
# 
# Input: nums = [1,2,3]
# Output: [[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]
# 
# 
# 
# Constraints:
# 
# 
# 1 <= nums.length <= 8
# -10 <= nums[i] <= 10
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def permuteUnique(self, nums: List[int]) -> List[List[int]]:
        """
        Interview explanation:
        Sort first so duplicate values are adjacent. During backtracking, skip
        nums[i] when it equals nums[i-1] and nums[i-1] has not been used in this
        position path; that means choosing nums[i] would create the same prefix
        as choosing the earlier equal value.

        Edge cases and tests:
        - [1,1,2] returns three unique permutations.
        - All equal values return one permutation.
        - The skip rule still allows duplicates when the previous copy is used.

        Complexity: O(U * n) time where U is the number of unique permutations,
        O(n) extra space excluding output.
        """
        nums.sort()
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
                if i > 0 and nums[i] == nums[i - 1] and not used[i - 1]:
                    continue
                used[i] = True
                path.append(val)
                dfs()
                path.pop()
                used[i] = False

        dfs()
        return ans
# @lc code=end


