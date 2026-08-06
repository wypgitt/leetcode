#
# @lc app=leetcode id=996 lang=python3
#
# [996] Number of Squareful Arrays
#
# https://leetcode.com/problems/number-of-squareful-arrays/description/
#
# algorithms
# Hard (51.7%)
# Likes:    1048
# Dislikes: 49
# Total Accepted:    52.0K
# Total Submissions: 101K
# Testcase Example:  "[1,17,8]"
#
# An array is squareful if the sum of every pair of adjacent elements is a
# perfect square.
#
# Given an integer array nums, return the number of permutations of nums that
# are squareful.
#
# Two permutations perm1 and perm2 are different if there is some index i such
# that perm1[i] != perm2[i].
#
# Example 1:
#
# Input: nums = [1,17,8]
# Output: 2
# Explanation: [1,8,17] and [17,8,1] are the valid permutations.
#
# Example 2:
#
# Input: nums = [2,2,2]
# Output: 1
#
# Constraints:
#
# 1 <= nums.length <= 12
#
# 0 <= nums[i] <= 10^9
#

# @lc code=start
import math
from collections import Counter
from typing import List, Optional


class Solution:
    def numSquarefulPerms(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Backtrack over permutations, only appending a number if previous+next
        is a perfect square. Deduplicate by counting frequencies (or skip equal
        unused values at the same depth).

        Algorithm (backtrack):
        - is_square(x): int(sqrt)^2 == x.
        - Build graph/count of values; dfs(prev, remaining Counter): if none
          left, +1; else for each distinct val with count>0, if prev is None or
          square(prev+val): use val, recurse, restore.
        - Start with prev=None.

        Complexity: O(n!) time worst, O(n) space.
        """
        def is_square(x: int) -> bool:
            r = int(math.isqrt(x))
            return r * r == x

        count = Counter(nums)
        ans = 0

        def dfs(prev: Optional[int], left: int) -> None:
            nonlocal ans
            if left == 0:
                ans += 1
                return
            for val in list(count.keys()):
                if count[val] == 0:
                    continue
                if prev is None or is_square(prev + val):
                    count[val] -= 1
                    dfs(val, left - 1)
                    count[val] += 1

        dfs(None, len(nums))
        return ans
# @lc code=end
