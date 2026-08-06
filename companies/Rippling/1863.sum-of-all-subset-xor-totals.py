#
# @lc app=leetcode id=1863 lang=python3
#
# [1863] Sum of All Subset XOR Totals
#
# https://leetcode.com/problems/sum-of-all-subset-xor-totals/description/
#
# algorithms
# Easy (90.1%)
# Likes:    2726
# Dislikes: 358
# Total Accepted:    372K
# Total Submissions: 413K
# Testcase Example:  "[1,3]"
#
# The XOR total of an array is defined as the bitwise XOR of all its elements,
# or 0 if the array is empty.
#
# For example, the XOR total of the array [2,5,6] is 2 XOR 5 XOR 6 = 1.
#
# Given an array nums, return the sum of all XOR totals for every subset of
# nums.
#
# Note: Subsets with the same elements should be counted multiple times.
#
# An array a is a subset of an array b if a can be obtained from b by deleting
# some (possibly zero) elements of b.
#
# Example 1:
#
# Input: nums = [1,3]
# Output: 6
# Explanation: The 4 subsets of [1,3] are:
# - The empty subset has an XOR total of 0.
# - [1] has an XOR total of 1.
# - [3] has an XOR total of 3.
# - [1,3] has an XOR total of 1 XOR 3 = 2.
# 0 + 1 + 3 + 2 = 6
#
# Example 2:
#
# Input: nums = [5,1,6]
# Output: 28
# Explanation: The 8 subsets of [5,1,6] are:
# - The empty subset has an XOR total of 0.
# - [5] has an XOR total of 5.
# - [1] has an XOR total of 1.
# - [6] has an XOR total of 6.
# - [5,1] has an XOR total of 5 XOR 1 = 4.
# - [5,6] has an XOR total of 5 XOR 6 = 3.
# - [1,6] has an XOR total of 1 XOR 6 = 7.
# - [5,1,6] has an XOR total of 5 XOR 1 XOR 6 = 2.
# 0 + 5 + 1 + 6 + 4 + 3 + 7 + 2 = 28
#
# Example 3:
#
# Input: nums = [3,4,5,6,7,8]
# Output: 480
# Explanation: The sum of all XOR totals for every subset is 480.
#
# Constraints:
#
# 1 <= nums.length <= 12
#
# 1 <= nums[i] <= 20
#

# @lc code=start
from typing import List


class Solution:
    def subsetXORSum(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Sum of XOR of every subset. Bit trick: each bit contributes independently;
        if any num has bit b, it appears in half of subsets → contrib =
        (bit) * 2^(n-1).

        Algorithm (bit contribution):
        - OR all nums → bits that appear; answer = OR * 2^(n-1).

        Complexity: O(n) time, O(1) space.
        """
        ors = 0
        for x in nums:
            ors |= x
        return ors << (len(nums) - 1)

    def subsetXORSum_dfs(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: DFS/backtracking over include/exclude each element.

        Algorithm:
        - dfs(i, xor): if i==n return xor; else dfs(i+1,xor)+dfs(i+1,xor^nums[i]).

        Complexity: O(2^n) time.
        """
        n = len(nums)

        def dfs(i: int, cur: int) -> int:
            if i == n:
                return cur
            return dfs(i + 1, cur) + dfs(i + 1, cur ^ nums[i])

        return dfs(0, 0)
# @lc code=end
