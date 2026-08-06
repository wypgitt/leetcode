#
# @lc app=leetcode id=1558 lang=python3
#
# [1558] Minimum Numbers of Function Calls to Make Target Array
#
# https://leetcode.com/problems/minimum-numbers-of-function-calls-to-make-target-array/description/
#
# algorithms
# Medium (62.74%)
# Likes:    654
# Dislikes: 38
# Total Accepted:    26.7K
# Total Submissions: 42.6K
# Testcase Example:  "[1,5]"
#
# You are given an integer array nums. You have an integer array arr of the
# same length with all values set to 0 initially. You also have the following
# modify function:
#
# You want to use the modify function to convert arr to nums using the minimum
# number of calls.
#
# Return the minimum number of function calls to make nums from arr.
#
# The test cases are generated so that the answer fits in a 32-bit signed
# integer.
#
# Example 1:
#
# Input: nums = [1,5]
# Output: 5
# Explanation: Increment by 1 (second element): [0, 0] to get [0, 1] (1
# operation).
# Double all the elements: [0, 1] -> [0, 2] -> [0, 4] (2 operations).
# Increment by 1 (both elements) [0, 4] -> [1, 4] -> [1, 5] (2 operations).
# Total of operations: 1 + 2 + 2 = 5.
#
# Example 2:
#
# Input: nums = [2,2]
# Output: 3
# Explanation: Increment by 1 (both elements) [0, 0] -> [0, 1] -> [1, 1] (2
# operations).
# Double all the elements: [1, 1] -> [2, 2] (1 operation).
# Total of operations: 2 + 1 = 3.
#
# Example 3:
#
# Input: nums = [4,2,5]
# Output: 6
# Explanation: (initial)[0,0,0] -> [1,0,0] -> [1,0,1] -> [2,0,2] -> [2,1,2] ->
# [4,2,4] -> [4,2,5](nums).
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 0 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def minOperations(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Start from zeros; ops: increment any element by 1, or double all.
        Reverse thinking: from nums, /2 all when even, else -1 some. Total =
        sum of set bits (increments) + (max bit-length - 1) doubles.

        Algorithm (bit count):
        - adds = sum(bin(x).count('1') for x in nums)
        - doubles = max(x.bit_length() for x in nums) - 1 (0 if all zero)
        - return adds + max(0, doubles)

        Complexity: O(n log A) time, O(1) space.
        """
        adds = 0
        max_len = 0
        for x in nums:
            adds += x.bit_count()
            max_len = max(max_len, x.bit_length())
        return adds + max(0, max_len - 1)

    def minOperations_simulate(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate reverse simulation: while any >0, if any odd decrement it
        (+1 op each), else divide all by 2 (+1 op).

        Algorithm:
        - Loop until all zero; count ops as above.

        Complexity: O(n log A).
        """
        arr = nums[:]
        ops = 0
        while any(arr):
            odd = False
            for i, x in enumerate(arr):
                if x % 2:
                    arr[i] -= 1
                    ops += 1
                    odd = True
            if not odd:
                for i in range(len(arr)):
                    arr[i] //= 2
                ops += 1
        return ops
# @lc code=end

