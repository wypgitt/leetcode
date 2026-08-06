#
# @lc app=leetcode id=491 lang=python3
#
# [491] Non-decreasing Subsequences
#
# https://leetcode.com/problems/non-decreasing-subsequences/description/
#
# algorithms
# Medium (62.94%)
# Likes:    3852
# Dislikes: 239
# Total Accepted:    217K
# Total Submissions: 345K
# Testcase Example:  "[4,6,7,7]"
#
# Given an integer array nums, return all the different possible non-decreasing
# subsequences of the given array with at least two elements. You may return
# the answer in any order.
#
# Example 1:
#
# Input: nums = [4,6,7,7]
# Output: [[4,6],[4,6,7],[4,6,7,7],[4,7],[4,7,7],[6,7],[6,7,7],[7,7]]
#
# Example 2:
#
# Input: nums = [4,4,3,2,1]
# Output: [[4,4]]
#
# Constraints:
#
# 1 <= nums.length <= 15
#
# -100 <= nums[i] <= 100
#

# @lc code=start
from typing import List


class Solution:
    def findSubsequences(self, nums: List[int]) -> List[List[int]]:
        """
        Interview explanation:
        Backtrack all non-decreasing subsequences of length ≥ 2. At each index,
        skip duplicates at the same depth (use a set of values chosen) so the
        same subsequence isn't built twice from different index picks.

        Algorithm:
        - DFS(start, path): if len(path)>=2: record copy.
          used = set(); for i in start..n-1: if nums[i] in used: continue;
          if path empty or nums[i] >= path[-1]: used.add; dfs(i+1, path+[nums[i]]).

        Complexity: O(2^n * n) time, O(n) recursion space (+ output).
        """
        ans = []
        n = len(nums)

        def dfs(start: int, path: List[int]) -> None:
            if len(path) >= 2:
                ans.append(path[:])
            used = set()
            for i in range(start, n):
                if nums[i] in used:
                    continue
                if not path or nums[i] >= path[-1]:
                    used.add(nums[i])
                    path.append(nums[i])
                    dfs(i + 1, path)
                    path.pop()

        dfs(0, [])
        return ans
# @lc code=end
