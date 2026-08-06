#
# @lc app=leetcode id=39 lang=python3
#
# [39] Combination Sum
#
# https://leetcode.com/problems/combination-sum/description/
#
# algorithms
# Medium (76.48%)
# Likes:    21029
# Dislikes: 542
# Total Accepted:    3.1M
# Total Submissions: 4.1M
# Testcase Example:  '[2,3,6,7]\n7'
#
# Given an array of distinct integers candidates and a target integer target,
# return a list of all unique combinations of candidates where the chosen
# numbers sum to target. You may return the combinations in any order.
# 
# The same number may be chosen from candidates an unlimited number of times.
# Two combinations are unique if the frequency of at least one of the chosen
# numbers is different.
# 
# The test cases are generated such that the number of unique combinations that
# sum up to target is less than 150 combinations for the given input.
# 
# 
# Example 1:
# 
# 
# Input: candidates = [2,3,6,7], target = 7
# Output: [[2,2,3],[7]]
# Explanation:
# 2 and 3 are candidates, and 2 + 2 + 3 = 7. Note that 2 can be used multiple
# times.
# 7 is a candidate, and 7 = 7.
# These are the only two combinations.
# 
# 
# Example 2:
# 
# 
# Input: candidates = [2,3,5], target = 8
# Output: [[2,2,2,2],[2,3,3],[3,5]]
# 
# 
# Example 3:
# 
# 
# Input: candidates = [2], target = 1
# Output: []
# 
# 
# 
# Constraints:
# 
# 
# 1 <= candidates.length <= 30
# 2 <= candidates[i] <= 40
# All elements of candidates are distinct.
# 1 <= target <= 40
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
        """
        Interview explanation:
        This is backtracking over choices with reuse allowed. Sorting lets us
        stop as soon as a candidate exceeds the remaining sum. Passing the start
        index prevents different orderings of the same combination.

        Edge cases and tests:
        - Candidate exactly equal to target forms a one-item answer.
        - Reuse is allowed, e.g. 2 can appear multiple times.
        - No possible combination returns [].

        Complexity: exponential in the number of combinations; recursion depth
        is at most target / min(candidates), excluding output storage.
        """
        candidates.sort()
        ans = []
        path = []

        def dfs(start: int, remain: int) -> None:
            if remain == 0:
                ans.append(path.copy())
                return
            for i in range(start, len(candidates)):
                val = candidates[i]
                if val > remain:
                    break
                path.append(val)
                dfs(i, remain - val)
                path.pop()

        dfs(0, target)
        return ans
# @lc code=end


