#
# @lc app=leetcode id=370 lang=python3
#
# [370] Range Addition
#
# https://leetcode.com/problems/range-addition/description/
#
# algorithms
# Medium (73.08%)
# Likes:    1687
# Dislikes: 86
# Total Accepted:    107.4K
# Total Submissions: 147K
# Testcase Example:  "5\n[[1,3,2],[2,4,3],[0,2,-2]]"
#
#
# You are given an integer length and an array updates where updates[i] =
# [startIdx_i, endIdx_i, inc_i].
#
# You have an array arr of length length with all zeros, and you have some
# operation to apply on arr. In the i^th operation, you should increment
# all the elements arr[startIdx_i], arr[startIdx_i + 1], ...,
# arr[endIdx_i] by inc_i.
#
# Return arr after applying all the updates.
#
# Example 1:
#
# Input: length = 5, updates = [[1,3,2],[2,4,3],[0,2,-2]]
# Output: [-2,0,3,5,3]
#
# Example 2:
#
# Input: length = 10, updates = [[2,4,6],[5,6,8],[1,9,-4]]
# Output: [0,-4,2,2,2,4,4,-4,-4,-4]
#
# Constraints:
#
# 1 <= length <= 10^5
#
# 0 <= updates.length <= 10^4
#
# 0 <= startIdx_i <= endIdx_i < length
#
# -1000 <= inc_i <= 1000
#
# @lc code=start
from typing import List


class Solution:
    def getModifiedArray(self, length: int, updates: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Difference array: for update [start, end, inc], add inc at start and
        -inc at end+1. Prefix sum reconstructs the final array in one pass.

        Algorithm:
        - diff = [0]*length.
        - For each update: diff[start]+=inc; if end+1 < length: diff[end+1]-=inc.
        - Prefix-sum diff in place; return.

        Complexity: O(length + updates) time, O(length) space.
        """
        diff = [0] * length
        for start, end, inc in updates:
            diff[start] += inc
            if end + 1 < length:
                diff[end + 1] -= inc
        for i in range(1, length):
            diff[i] += diff[i - 1]
        return diff
# @lc code=end
