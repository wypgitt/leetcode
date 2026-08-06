#
# @lc app=leetcode id=3152 lang=python3
#
# [3152] Special Array II
#
# https://leetcode.com/problems/special-array-ii/description/
#
# algorithms
# Medium (45.75%)
# Likes:    921
# Dislikes: 67
# Total Accepted:    139.5K
# Total Submissions: 304.9K
# Testcase Example:  "[3,4,1,2,6]\n[[0,4]]"
#
#
# An array is considered special if every pair of its adjacent elements
# contains two numbers with different parity.
#
# You are given an array of integer nums and a 2D integer matrix queries,
# where for queries[i] = [from_i, to_i] your task is to check that
# subarray nums[from_i..to_i] is special or not.
#
# Return an array of booleans answer such that answer[i] is true if
# nums[from_i..to_i] is special.
#
# Example 1:
#
# Input: nums = [3,4,1,2,6], queries = [[0,4]]
#
# Output: [false]
#
# Explanation:
#
# The subarray is [3,4,1,2,6]. 2 and 6 are both even.
#
# Example 2:
#
# Input: nums = [4,3,1,6], queries = [[0,2],[2,3]]
#
# Output: [false,true]
#
# Explanation:
#
# The subarray is [4,3,1]. 3 and 1 are both odd. So the answer to this
# query is false.
#
# The subarray is [1,6]. There is only one pair: (1,6) and it contains
# numbers with different parity. So the answer to this query is true.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#
# 1 <= queries.length <= 10^5
#
# queries[i].length == 2
#
# 0 <= queries[i][0] <= queries[i][1] <= nums.length - 1
#

# @lc code=start
from typing import List


class Solution:
    def isArraySpecial(self, nums: List[int], queries: List[List[int]]) -> List[bool]:
        """
        Interview explanation:
        A subarray is special iff every adjacent pair has different parity.
        Answer many range queries efficiently.

        Algorithm:
        - bad[i] = 1 if nums[i] and nums[i+1] share parity.
        - Prefix sums of bad; range [L,R] is special iff no bad edge in [L, R-1].

        Complexity: O(n + q) time, O(n) space.
        """
        n = len(nums)
        pref = [0] * n
        for i in range(n - 1):
            pref[i + 1] = pref[i] + (
                0 if (nums[i] ^ nums[i + 1]) & 1 else 1
            )
        return [pref[r] - pref[l] == 0 for l, r in queries]
# @lc code=end
