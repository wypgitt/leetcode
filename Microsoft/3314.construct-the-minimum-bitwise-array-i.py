#
# @lc app=leetcode id=3314 lang=python3
#
# [3314] Construct the Minimum Bitwise Array I
#
# https://leetcode.com/problems/construct-the-minimum-bitwise-array-i/description/
#
# algorithms
# Easy (85.27%)
# Likes:    425
# Dislikes: 53
# Total Accepted:    140.4K
# Total Submissions: 164.7K
# Testcase Example:  "[2,3,5,7]"
#
#
# You are given an array nums consisting of n prime integers.
#
# You need to construct an array ans of length n, such that, for each
# index i, the bitwise OR of ans[i] and ans[i] + 1 is equal to nums[i],
# i.e. ans[i] OR (ans[i] + 1) == nums[i].
#
# Additionally, you must minimize each value of ans[i] in the resulting
# array.
#
# If it is not possible to find such a value for ans[i] that satisfies the
# condition, then set ans[i] = -1.
#
# Example 1:
#
# Input: nums = [2,3,5,7]
#
# Output: [-1,1,4,3]
#
# Explanation:
#
# For i = 0, as there is no value for ans[0] that satisfies ans[0] OR
# (ans[0] + 1) = 2, so ans[0] = -1.
#
# For i = 1, the smallest ans[1] that satisfies ans[1] OR (ans[1] + 1) = 3
# is 1, because 1 OR (1 + 1) = 3.
#
# For i = 2, the smallest ans[2] that satisfies ans[2] OR (ans[2] + 1) = 5
# is 4, because 4 OR (4 + 1) = 5.
#
# For i = 3, the smallest ans[3] that satisfies ans[3] OR (ans[3] + 1) = 7
# is 3, because 3 OR (3 + 1) = 7.
#
# Example 2:
#
# Input: nums = [11,13,31]
#
# Output: [9,12,15]
#
# Explanation:
#
# For i = 0, the smallest ans[0] that satisfies ans[0] OR (ans[0] + 1) =
# 11 is 9, because 9 OR (9 + 1) = 11.
#
# For i = 1, the smallest ans[1] that satisfies ans[1] OR (ans[1] + 1) =
# 13 is 12, because 12 OR (12 + 1) = 13.
#
# For i = 2, the smallest ans[2] that satisfies ans[2] OR (ans[2] + 1) =
# 31 is 15, because 15 OR (15 + 1) = 31.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 2 <= nums[i] <= 1000
#
# nums[i] is a prime number.
#

# @lc code=start
from typing import List


class Solution:
    def minBitwiseArray(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        For each prime nums[i], find minimal ans such that ans | (ans + 1) == nums[i].
        x | (x + 1) is always odd (fills trailing zeros of x), so evens -> -1.

        Algorithm:
        - If n even: -1. Else let t = trailing ones of n; answer n XOR 2^(t-1)
          (clear the highest bit in the trailing-ones block).

        Complexity: O(n log A) time, O(1) extra space.
        """
        def f(n: int) -> int:
            if n % 2 == 0:
                return -1
            t = 0
            x = n
            while x & 1:
                t += 1
                x >>= 1
            return n ^ (1 << (t - 1))

        return [f(x) for x in nums]

    def minBitwiseArray_scan(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Tiny bounds (nums[i] <= 1000): scan candidates upward.

        Algorithm:
        - For each n, try ans from 0..n-1 until ans | (ans+1) == n.

        Complexity: O(n * A) time, O(1) space.
        """
        ans = []
        for n in nums:
            found = -1
            for x in range(n):
                if x | (x + 1) == n:
                    found = x
                    break
            ans.append(found)
        return ans
# @lc code=end
