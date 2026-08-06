#
# @lc app=leetcode id=3630 lang=python3
#
# [3630] Partition Array for Maximum XOR and AND
#
# https://leetcode.com/problems/partition-array-for-maximum-xor-and-and/description/
#
# algorithms
# Hard (17.70%)
# Likes:    34
# Dislikes: 8
# Total Accepted:    7.6K
# Total Submissions: 42.8K
# Testcase Example:  "[2,3]"
#
#
# You are given an integer array nums.
#
# Partition the array into three (possibly empty) subsequences A, B, and C
# such that every element of nums belongs to exactly one subsequence.
#
# Your goal is to maximize the value of: XOR(A) + AND(B) + XOR(C)
#
# where:
#
# XOR(arr) denotes the bitwise XOR of all elements in arr. If arr is
# empty, its value is defined as 0.
#
# AND(arr) denotes the bitwise AND of all elements in arr. If arr is
# empty, its value is defined as 0.
#
# Return the maximum value achievable.
#
# Note: If multiple partitions result in the same maximum sum, you can
# consider any one of them.
#
# Example 1:
#
# Input: nums = [2,3]
#
# Output: 5
#
# Explanation:
#
# One optimal partition is:
#
# A = [3], XOR(A) = 3
#
# B = [2], AND(B) = 2
#
# C = [], XOR(C) = 0
#
# The maximum value of: XOR(A) + AND(B) + XOR(C) = 3 + 2 + 0 = 5. Thus,
# the answer is 5.
#
# Example 2:
#
# Input: nums = [1,3,2]
#
# Output: 6
#
# Explanation:
#
# One optimal partition is:
#
# A = [1], XOR(A) = 1
#
# B = [2], AND(B) = 2
#
# C = [3], XOR(C) = 3
#
# The maximum value of: XOR(A) + AND(B) + XOR(C) = 1 + 2 + 3 = 6. Thus,
# the answer is 6.
#
# Example 3:
#
# Input: nums = [2,3,6,7]
#
# Output: 15
#
# Explanation:
#
# One optimal partition is:
#
# A = [7], XOR(A) = 7
#
# B = [2,3], AND(B) = 2
#
# C = [6], XOR(C) = 6
#
# The maximum value of: XOR(A) + AND(B) + XOR(C) = 7 + 2 + 6 = 15. Thus,
# the answer is 15.
#
# Constraints:
#
# 1 <= nums.length <= 19
#
# 1 <= nums[i] <= 10^9
#

# @lc code=start

from typing import List


class Solution:
    def maximizeXorAndXor(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Maximize XOR(A)+AND(B)+XOR(C). Enumerate subset B (n<=19). For the
        remaining multiset S with XOR = X, max XOR(A)+XOR(C) over partitions
        of S equals X + 2*max_xor_subset({x & ~X}), via GF(2) linear basis.

        Algorithm:
        - Precompute AND and XOR for every bitmask subset.
        - For each mask as B: ans = max(ans, AND(B) + XOR(S) + 2*max_xor).
        - Include empty B (AND=0).

        Complexity: O(n * 2^n * log A) time, O(2^n) space.
        """
        def max_xor_subset(vals) -> int:
            base = [0] * bit_len
            for x in vals:
                for i in range(bit_len - 1, -1, -1):
                    if not x & (1 << i):
                        continue
                    if base[i] == 0:
                        base[i] = x
                        break
                    x ^= base[i]
            best = 0
            for b in reversed(base):
                if (best ^ b) > best:
                    best ^= b
            return best

        bit_len = max(nums).bit_length()
        n = len(nums)
        and_arr = [0] * (1 << n)
        xor_arr = [0] * (1 << n)
        for mask in range(1, 1 << n):
            lb = mask & -mask
            i = lb.bit_length() - 1
            prev = mask ^ lb
            and_arr[mask] = and_arr[prev] & nums[i] if prev else nums[i]
            xor_arr[mask] = xor_arr[prev] ^ nums[i]

        full = (1 << n) - 1
        ans = 0
        for mask in range(1 << n):
            total_and = and_arr[mask]
            total_xor = xor_arr[full ^ mask]
            mx = max_xor_subset(
                nums[i] & ~total_xor for i in range(n) if not (mask & (1 << i))
            )
            ans = max(ans, total_and + total_xor + 2 * mx)
        return ans
# @lc code=end

