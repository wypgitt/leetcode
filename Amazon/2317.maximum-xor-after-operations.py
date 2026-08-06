#
# @lc app=leetcode id=2317 lang=python3
#
# [2317] Maximum XOR After Operations 
#
# https://leetcode.com/problems/maximum-xor-after-operations/description/
#
# algorithms
# Medium (79.86%)
# Likes:    654
# Dislikes: 171
# Total Accepted:    32.9K
# Total Submissions: 41.2K
# Testcase Example:  "[3,2,4,6]"
#
# You are given a 0-indexed integer array nums. In one operation, select any
# non-negative integer x and an index i, then update nums[i] to be equal to
# nums[i] AND (nums[i] XOR x).
#
# Note that AND is the bitwise AND operation and XOR is the bitwise XOR
# operation.
#
# Return the maximum possible bitwise XOR of all elements of nums after applying
# the operation any number of times.
#
#
#
# Example 1:
#
# Input: nums = [3,2,4,6]
# Output: 7
# Explanation: Apply the operation with x = 4 and i = 3, num[3] = 6 AND (6 XOR
# 4) = 6 AND 2 = 2.
# Now, nums = [3, 2, 4, 2] and the bitwise XOR of all the elements = 3 XOR 2 XOR
# 4 XOR 2 = 7.
# It can be shown that 7 is the maximum possible bitwise XOR.
# Note that other operations may be used to achieve a bitwise XOR of 7.
#
# Example 2:
#
# Input: nums = [1,2,3,9,2]
# Output: 11
# Explanation: Apply the operation zero times.
# The bitwise XOR of all the elements = 1 XOR 2 XOR 3 XOR 9 XOR 2 = 11.
# It can be shown that 11 is the maximum possible bitwise XOR.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 0 <= nums[i] <= 10^8
#

# @lc code=start
from typing import List
from functools import reduce
import operator


class Solution:
    def maximumXOR(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Operation: nums[i] &= (nums[i] XOR x) for any x — can turn off bits of
        nums[i] but never turn on. Maximize bitwise XOR of all nums after ops.

        Algorithm:
        - Since we can freely clear bits in each number, any bit that appears
          in any number can be kept in the XOR (by clearing elsewhere). Answer
          is bitwise OR of all numbers.

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        for x in nums:
            ans |= x
        return ans

    def maximumXOR_bit(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Bitwise OR insight (same as primary).

        Algorithm:
        - OR-reduce the array.

        Complexity: O(n) time, O(1) space.
        """
        return reduce(operator.or_, nums, 0)
# @lc code=end
