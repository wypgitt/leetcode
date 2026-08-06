#
# @lc app=leetcode id=40 lang=python3
#
# [40] Combination Sum II
#
# https://leetcode.com/problems/combination-sum-ii/description/
#
# algorithms
# Medium (59.41%)
# Likes:    12298
# Dislikes: 390
# Total Accepted:    1.7M
# Total Submissions: 2.9M
# Testcase Example:  '[10,1,2,7,6,1,5]\n8'
#
# Given a collection of candidate numbers (candidates) and a target number
# (target), find all unique combinations in candidates where the candidate
# numbers sum to target.
# 
# Each number in candidates may only be used once in the combination.
# 
# Note: The solution set must not contain duplicate combinations.
# 
# 
# Example 1:
# 
# 
# Input: candidates = [10,1,2,7,6,1,5], target = 8
# Output: 
# [
# [1,1,6],
# [1,2,5],
# [1,7],
# [2,6]
# ]
# 
# 
# Example 2:
# 
# 
# Input: candidates = [2,5,2,1,2], target = 5
# Output: 
# [
# [1,2,2],
# [5]
# ]
# 
# 
# 
# Constraints:
# 
# 
# 1 <= candidates.length <= 100
# 1 <= candidates[i] <= 50
# 1 <= target <= 30
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def combinationSum2(self, candidates: List[int], target: int) -> List[List[int]]:
        """
        Interview explanation:
        Each candidate can be used once, and duplicates in the input must not
        create duplicate combinations. Sorting groups equal values together; at
        each recursion depth, skip a value equal to the previous value already
        considered at that same depth.

        Edge cases and tests:
        - Duplicate candidates like [1,1,2] produce [1,2] once.
        - Candidate exactly equal to remaining sum is valid.
        - Values larger than remain can stop the loop after sorting.

        Complexity: O(2^n * n) worst-case time including output copies, O(n)
        recursion space.
        """
        candidates.sort()
        ans = []
        path = []

        def dfs(start: int, remain: int) -> None:
            if remain == 0:
                ans.append(path.copy())
                return
            prev = None
            for i in range(start, len(candidates)):
                val = candidates[i]
                if val == prev:
                    continue
                if val > remain:
                    break
                path.append(val)
                dfs(i + 1, remain - val)
                path.pop()
                prev = val

        dfs(0, target)
        return ans
# @lc code=end


