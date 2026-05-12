#
# @lc app=leetcode id=1310 lang=python3
#
# [1310] XOR Queries of a Subarray
#
# https://leetcode.com/problems/xor-queries-of-a-subarray/description/
#
# algorithms
# Medium (78.06%)
# Likes:    2107
# Dislikes: 61
# Total Accepted:    218.4K
# Total Submissions: 279.8K
# Testcase Example:  '[1,3,4,8]\n[[0,1],[1,2],[0,3],[3,3]]'
#
# You are given an array arr of positive integers. You are also given the array
# queries where queries[i] = [lefti, righti].
# 
# For each query i compute the XOR of elements from lefti to righti (that is,
# arr[lefti] XOR arr[lefti + 1] XOR ... XOR arr[righti] ).
# 
# Return an array answer where answer[i] is the answer to the i^th query.
# 
# 
# Example 1:
# 
# 
# Input: arr = [1,3,4,8], queries = [[0,1],[1,2],[0,3],[3,3]]
# Output: [2,7,14,8] 
# Explanation: 
# The binary representation of the elements in the array are:
# 1 = 0001 
# 3 = 0011 
# 4 = 0100 
# 8 = 1000 
# The XOR values for queries are:
# [0,1] = 1 xor 3 = 2 
# [1,2] = 3 xor 4 = 7 
# [0,3] = 1 xor 3 xor 4 xor 8 = 14 
# [3,3] = 8
# 
# 
# Example 2:
# 
# 
# Input: arr = [4,8,2,10], queries = [[2,3],[1,3],[0,0],[0,3]]
# Output: [8,0,4,4]
# 
# 
# 
# Constraints:
# 
# 
# 1 <= arr.length, queries.length <= 3 * 10^4
# 1 <= arr[i] <= 10^9
# queries[i].length == 2
# 0 <= lefti <= righti < arr.length
# 
# 
#

# @lc code=start
from __future__ import annotations

from typing import List


class Solution:
    def xorQueries(self, arr: List[int], queries: List[List[int]]) -> List[int]:
        prefix = [0]
        for num in arr:
            prefix.append(prefix[-1] ^ num)

        return [prefix[right + 1] ^ prefix[left] for left, right in queries]
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# XOR has the same cancellation property that prefix sums use:
# `x ^ x = 0` and `x ^ 0 = x`. If `prefix[i]` is the XOR of `arr[0:i]`, then
# the XOR of `arr[left:right+1]` is `prefix[right+1] ^ prefix[left]`.
#
# Data structure:
# A prefix XOR array of length `n + 1`. The leading 0 makes ranges beginning at
# index 0 work without special casing.
#
# Walkthrough:
# 1. Build `prefix`, where each new entry XORs the next array value.
# 2. For each query, XOR the prefix before the range with the prefix after the
#    range. Values before `left` appear twice and cancel out.
#
# Edge cases:
# - Query starts at 0: `prefix[0]` is 0.
# - Single-element query: `prefix[i+1] ^ prefix[i]` returns that element.
# - Repeated values: XOR cancellation handles them correctly.
#
# Complexity:
# - Time: O(n + q), where q is the number of queries.
# - Space: O(n) for the prefix array, excluding the output.
