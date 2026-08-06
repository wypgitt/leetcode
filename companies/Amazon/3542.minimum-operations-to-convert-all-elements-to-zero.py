#
# @lc app=leetcode id=3542 lang=python3
#
# [3542] Minimum Operations to Convert All Elements to Zero
#
# https://leetcode.com/problems/minimum-operations-to-convert-all-elements-to-zero/description/
#
# algorithms
# Medium (53.08%)
# Likes:    626
# Dislikes: 64
# Total Accepted:    89.3K
# Total Submissions: 168.2K
# Testcase Example:  "[0,2]"
#
#
# You are given an array nums of size n, consisting of non-negative
# integers. Your task is to apply some (possibly zero) operations on the
# array so that all elements become 0.
#
# In one operation, you can select a subarray [i, j] (where 0 <= i <= j <
# n) and set all occurrences of the minimum non-negative integer in that
# subarray to 0.
#
# Return the minimum number of operations required to make all elements in
# the array 0.
#
# Example 1:
#
# Input: nums = [0,2]
#
# Output: 1
#
# Explanation:
#
# Select the subarray [1,1] (which is [2]), where the minimum non-negative
# integer is 2. Setting all occurrences of 2 to 0 results in [0,0].
#
# Thus, the minimum number of operations required is 1.
#
# Example 2:
#
# Input: nums = [3,1,2,1]
#
# Output: 3
#
# Explanation:
#
# Select subarray [1,3] (which is [1,2,1]), where the minimum non-negative
# integer is 1. Setting all occurrences of 1 to 0 results in [3,0,2,0].
#
# Select subarray [2,2] (which is [2]), where the minimum non-negative
# integer is 2. Setting all occurrences of 2 to 0 results in [3,0,0,0].
#
# Select subarray [0,0] (which is [3]), where the minimum non-negative
# integer is 3. Setting all occurrences of 3 to 0 results in [0,0,0,0].
#
# Thus, the minimum number of operations required is 3.
#
# Example 3:
#
# Input: nums = [1,2,1,2,1,2]
#
# Output: 4
#
# Explanation:
#
# Select subarray [0,5] (which is [1,2,1,2,1,2]), where the minimum
# non-negative integer is 1. Setting all occurrences of 1 to 0 results in
# [0,2,0,2,0,2].
#
# Select subarray [1,1] (which is [2]), where the minimum non-negative
# integer is 2. Setting all occurrences of 2 to 0 results in
# [0,0,0,2,0,2].
#
# Select subarray [3,3] (which is [2]), where the minimum non-negative
# integer is 2. Setting all occurrences of 2 to 0 results in
# [0,0,0,0,0,2].
#
# Select subarray [5,5] (which is [2]), where the minimum non-negative
# integer is 2. Setting all occurrences of 2 to 0 results in
# [0,0,0,0,0,0].
#
# Thus, the minimum number of operations required is 4.
#
# Constraints:
#
# 1 <= n == nums.length <= 10^5
#
# 0 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def minOperations(self, nums: List[int]) -> int:
        """
        Interview explanation:
        An operation zeroes every occurrence of the current subarray minimum.
        Distinct increasing layers of positive values each need their own op;
        zeros reset the active stack.

        Algorithm (monotonic stack):
        - Scan left to right with a strictly increasing stack of positive values.
        - On 0, clear the stack.
        - When pushing a new value above the (possibly trimmed) top, +1 operation.
        - Equal to the top means this value is already covered by a prior op.

        Complexity: O(n) time, O(n) space.
        """
        stack: List[int] = []
        ops = 0
        for x in nums:
            if x == 0:
                stack.clear()
                continue
            while stack and stack[-1] > x:
                stack.pop()
            if not stack or stack[-1] < x:
                ops += 1
                stack.append(x)
        return ops
# @lc code=end
