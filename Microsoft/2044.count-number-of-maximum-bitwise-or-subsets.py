#
# @lc app=leetcode id=2044 lang=python3
#
# [2044] Count Number of Maximum Bitwise-OR Subsets
#
# https://leetcode.com/problems/count-number-of-maximum-bitwise-or-subsets/description/
#
# algorithms
# Medium (89.47%)
# Likes:    1418
# Dislikes: 98
# Total Accepted:    253.1K
# Total Submissions: 282.9K
# Testcase Example:  "[3,1]"
#
# Given an integer array nums, find the maximum possible bitwise OR of a subset
# of nums and return the number of different non-empty subsets with the maximum
# bitwise OR.
#
# An array a is a subset of an array b if a can be obtained from b by deleting
# some (possibly zero) elements of b. Two subsets are considered different if
# the indices of the elements chosen are different.
#
# The bitwise OR of an array a is equal to a[0] OR a[1] OR ... OR a[a.length -
# 1] (0-indexed).
#
#
#
# Example 1:
#
# Input: nums = [3,1]
# Output: 2
# Explanation: The maximum possible bitwise OR of a subset is 3. There are 2
# subsets with a bitwise OR of 3:
# - [3]
# - [3,1]
#
# Example 2:
#
# Input: nums = [2,2,2]
# Output: 7
# Explanation: All non-empty subsets of [2,2,2] have a bitwise OR of 2. There
# are 2^3 - 1 = 7 total subsets.
#
# Example 3:
#
# Input: nums = [3,2,1,5]
# Output: 6
# Explanation: The maximum possible bitwise OR of a subset is 7. There are 6
# subsets with a bitwise OR of 7:
# - [3,5]
# - [3,1,5]
# - [3,2,5]
# - [3,2,1,5]
# - [2,5]
# - [2,1,5]
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 16
#
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def countMaxOrSubsets(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Count nonempty subsets whose bitwise OR equals the global maximum OR
        (OR of all elements). n <= 16 → subset enumeration.

        Algorithm:
        - target = OR of all; iterate nonempty masks; count OR == target.

        Complexity: O(n * 2^n) time, O(1) space.
        """
        n = len(nums)
        target = 0
        for x in nums:
            target |= x
        ans = 0
        for mask in range(1, 1 << n):
            cur = 0
            for i in range(n):
                if mask & (1 << i):
                    cur |= nums[i]
            if cur == target:
                ans += 1
        return ans

    def countMaxOrSubsets_dfs(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Classic alternate DFS/backtracking over include/exclude.

        Algorithm:
        - Recurse index; when reaching end, count if OR equals target (nonempty
          via starting from choices that take at least one, or check mask).

        Complexity: O(2^n) time, O(n) space.
        """
        target = 0
        for x in nums:
            target |= x
        self.ans = 0

        def dfs(i: int, cur: int, taken: bool) -> None:
            if i == len(nums):
                if taken and cur == target:
                    self.ans += 1
                return
            dfs(i + 1, cur | nums[i], True)
            dfs(i + 1, cur, taken)

        dfs(0, 0, False)
        return self.ans
# @lc code=end
