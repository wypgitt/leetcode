#
# @lc app=leetcode id=2599 lang=python3
#
# [2599] Make the Prefix Sum Non-negative
#
# https://leetcode.com/problems/make-the-prefix-sum-non-negative/description/
#
# algorithms
# Medium (51.94%)
# Likes:    99
# Dislikes: 3
# Total Accepted:    8.6K
# Total Submissions: 16.5K
# Testcase Example:  "[2,3,-5,4]"
#
#
# You are given a 0-indexed integer array nums. You can apply the
# following operation any number of times:
#
# Pick any element from nums and put it at the end of nums.
#
# The prefix sum array of nums is an array prefix of the same length as
# nums such that prefix[i] is the sum of all the integers nums[j] where j
# is in the inclusive range [0, i].
#
# Return the minimum number of operations such that the prefix sum array
# does not contain negative integers. The test cases are generated such
# that it is always possible to make the prefix sum array non-negative.
#
# Example 1:
#
# Input: nums = [2,3,-5,4]
# Output: 0
# Explanation: we do not need to do any operations.
# The array is [2,3,-5,4]. The prefix sum array is [2, 5, 0, 4].
#
# Example 2:
#
# Input: nums = [3,-5,-2,6]
# Output: 1
# Explanation: we can do one operation on index 1.
# The array after the operation is [3,-2,6,-5]. The prefix sum array is
# [3, 1, 7, 2].
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -10^9 <= nums[i] <= 10^9
#
# @lc code=start
from typing import List
import heapq


class Solution:
    def makePrefSumNonNegative(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Move elements to the end (each move is one operation) so every prefix sum is
        non-negative; minimize operations.

        Algorithm:
        - Scan left to right with running sum; keep a min-heap of negative numbers used.
        - When sum < 0, move the most negative number seen so far to the end (pop heap,
          subtract it from sum / add its absolute), increment ops.

        Complexity: O(n log n) time, O(n) space.
        """
        s = 0
        ops = 0
        h = []
        for x in nums:
            s += x
            if x < 0:
                heapq.heappush(h, x)
            while s < 0 and h:
                s -= heapq.heappop(h)
                ops += 1
        return ops
# @lc code=end
