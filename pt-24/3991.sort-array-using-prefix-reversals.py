#
# @lc app=leetcode id=3991 lang=python3
#
# [3991] Sort Array Using Prefix Reversals
#
# https://leetcode.com/problems/sort-array-using-prefix-reversals/description/
#
# algorithms
# Medium (70.48%)
# Likes:    5
# Dislikes: 1
# Total Accepted:    265
# Total Submissions: 376
# Testcase Example:  "[2,0,1]\n[2,3]"
#
#
# You are given an integer array nums of length n, where nums is a
# permutation of the integers in the range [0, n - 1].
#
# You are also given an integer array pre, where each pre[i] is a valid
# prefix length.
#
# In one operation, you may choose any length x from pre and reverse the
# first x elements of nums.
#
# For example, applying a prefix reversal of length 3 on [4, 1, 2, 3]
# results in [2, 1, 4, 3].
#
# Return the minimum number of operations required to sort nums in
# ascending order. If it is impossible to sort nums, return -1.
#
# Example 1:
#
# Input: nums = [2,0,1], pre = [2,3]
#
# Output: 2
#
# Explanation:
#
# Reverse pre[1] = 3 elements to get nums = [1, 0, 2].
#
# Then reverse pre[0] = 2 elements to get nums = [0, 1, 2].
#
# Thus, the minimum number of prefix reversal required is 2.
#
# Example 2:
#
# Input: nums = [1,0,2], pre = [1,3]
#
# Output: -1
#
# Explanation:
#
# It is impossible to sort the array using the given prefix lengths, so
# the answer is -1.
#
# Example 3:
#
# Input: nums = [0,1], pre = [2]
#
# Output: 0
#
# Explanation:
#
# Since nums is already sorted, no prefix reversals are needed. Thus, the
# answer is 0.
#
# Constraints:
#
# 1 <= n == nums.length <= 8
#
# 0 <= nums[i] <= n - 1
#
# 1 <= pre.length <= n
#
# 1 <= pre[i] <= n
#
# ​​​​​​​nums is a permutation of integers from 0 to n - 1.
#
# pre consists of unique integers.
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def sortArray(self, nums: List[int], pre: List[int]) -> int:
        """
        Interview explanation:
        nums is a permutation of 0..n-1 (n <= 8). Allowed moves are prefix
        reversals of lengths in pre. BFS the permutation graph for the
        shortest path to sorted order.

        Algorithm:
        - State = tuple(nums). BFS from the start; for each pre length reverse
          that prefix. Return distance when sorted, else -1.

        Complexity: O(n! * |pre| * n) time/space with n <= 8.
        """
        n = len(nums)
        target = tuple(range(n))
        start = tuple(nums)
        if start == target:
            return 0

        vis = {start}
        q = deque([(start, 0)])
        while q:
            state, dist = q.popleft()
            nd = dist + 1
            for x in pre:
                nxt = state[:x][::-1] + state[x:]
                if nxt == target:
                    return nd
                if nxt not in vis:
                    vis.add(nxt)
                    q.append((nxt, nd))
        return -1
# @lc code=end
