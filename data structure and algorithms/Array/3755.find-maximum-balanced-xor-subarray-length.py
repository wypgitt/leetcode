#
# @lc app=leetcode id=3755 lang=python3
#
# [3755] Find Maximum Balanced XOR Subarray Length
#
# https://leetcode.com/problems/find-maximum-balanced-xor-subarray-length/description/
#
# algorithms
# Medium (50.50%)
# Likes:    116
# Dislikes: 6
# Total Accepted:    19.8K
# Total Submissions: 39.2K
# Testcase Example:  "[3,1,3,2,0]"
#
#
# Given an integer array nums, return the length of the longest subarray
# that has a bitwise XOR of zero and contains an equal number of even and
# odd numbers. If no such subarray exists, return 0.
#
# Example 1:
#
# Input: nums = [3,1,3,2,0]
#
# Output: 4
#
# Explanation:
#
# The subarray [1, 3, 2, 0] has bitwise XOR 1 XOR 3 XOR 2 XOR 0 = 0 and
# contains 2 even and 2 odd numbers.
#
# Example 2:
#
# Input: nums = [3,2,8,5,4,14,9,15]
#
# Output: 8
#
# Explanation:
#
# The whole array has bitwise XOR 0 and contains 4 even and 4 odd numbers.
#
# Example 3:
#
# Input: nums = [0]
#
# Output: 0
#
# Explanation:
#
# No non-empty subarray satisfies both conditions.
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
    def maxBalancedSubarray(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Need XOR 0 and equal #even/#odd. Equal parity counts iff a +1/-1 balance
        returns to the same value; XOR 0 iff prefix XOR matches.

        Algorithm:
        - Track prefix XOR and balance (#odd - #even). Map (xor, bal) -> earliest
          index; maximize j - i when the pair repeats.

        Complexity: O(n) time, O(n) space.
        """
        first = {(0, 0): -1}
        pxor = bal = 0
        ans = 0
        for i, x in enumerate(nums):
            pxor ^= x
            bal += 1 if x % 2 else -1
            key = (pxor, bal)
            if key in first:
                ans = max(ans, i - first[key])
            else:
                first[key] = i
        return ans
# @lc code=end
