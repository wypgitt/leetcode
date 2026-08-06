#
# @lc app=leetcode id=3287 lang=python3
#
# [3287] Find the Maximum Sequence Value of Array
#
# https://leetcode.com/problems/find-the-maximum-sequence-value-of-array/description/
#
# algorithms
# Hard (22.22%)
# Likes:    92
# Dislikes: 9
# Total Accepted:    6.3K
# Total Submissions: 28.5K
# Testcase Example:  "[2,6,7]\n1"
#
#
# You are given an integer array nums and a positive integer k.
#
# The value of a sequence seq of size 2 * x is defined as:
#
# (seq[0] OR seq[1] OR ... OR seq[x - 1]) XOR (seq[x] OR seq[x + 1] OR ...
# OR seq[2 * x - 1]).
#
# Return the maximum value of any subsequence of nums having size 2 * k.
#
# Example 1:
#
# Input: nums = [2,6,7], k = 1
#
# Output: 5
#
# Explanation:
#
# The subsequence [2, 7] has the maximum value of 2 XOR 7 = 5.
#
# Example 2:
#
# Input: nums = [4,2,5,6,7], k = 2
#
# Output: 2
#
# Explanation:
#
# The subsequence [4, 5, 6, 7] has the maximum value of (4 OR 5) XOR (6 OR
# 7) = 2.
#
# Constraints:
#
# 2 <= nums.length <= 400
#
# 1 <= nums[i] < 2^7
#
# 1 <= k <= nums.length / 2
#

# @lc code=start
from typing import List


class Solution:
    def maxValue(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Subsequence of length 2k; value = (OR of first k) XOR (OR of last k).
        Values < 2^7 so OR-state sets are tiny bitmasks.

        Algorithm:
        - DP bitsets: left[i][j] = possible ORs with j picks from nums[:i].
        - right[i][j] similarly from nums[i:].
        - For each split mid, maximize a XOR b over left[mid][k] x right[mid][k].

        Complexity: O(n * k * 2^7) time, O(n * k) space.
        """
        n = len(nums)

        def build_forward() -> List[List[int]]:
            f = [[0] * (k + 1) for _ in range(n + 1)]
            f[0][0] = 1
            for i in range(n):
                x = nums[i]
                for j in range(k + 1):
                    f[i + 1][j] |= f[i][j]
                    if j < k:
                        m = f[i][j]
                        add = 0
                        while m:
                            b = (m & -m).bit_length() - 1
                            add |= 1 << (b | x)
                            m &= m - 1
                        f[i + 1][j + 1] |= add
            return f

        left = build_forward()
        right = [[0] * (k + 1) for _ in range(n + 1)]
        right[n][0] = 1
        for i in range(n - 1, -1, -1):
            x = nums[i]
            for j in range(k + 1):
                right[i][j] |= right[i + 1][j]
                if j < k:
                    m = right[i + 1][j]
                    add = 0
                    while m:
                        b = (m & -m).bit_length() - 1
                        add |= 1 << (b | x)
                        m &= m - 1
                    right[i][j + 1] |= add

        ans = 0
        for mid in range(k, n - k + 1):
            A, B = left[mid][k], right[mid][k]
            a_vals = []
            m = A
            while m:
                b = (m & -m).bit_length() - 1
                a_vals.append(b)
                m &= m - 1
            m = B
            while m:
                b = (m & -m).bit_length() - 1
                for a in a_vals:
                    if a ^ b > ans:
                        ans = a ^ b
                m &= m - 1
        return ans
# @lc code=end
