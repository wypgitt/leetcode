#
# @lc app=leetcode id=3821 lang=python3
#
# [3821] Find Nth Smallest Integer With K One Bits
#
# https://leetcode.com/problems/find-nth-smallest-integer-with-k-one-bits/description/
#
# algorithms
# Hard (35.41%)
# Likes:    71
# Dislikes: 2
# Total Accepted:    10.2K
# Total Submissions: 28.8K
# Testcase Example:  "4\n2"
#
#
# You are given two positive integers n and k.
#
# Return an integer denoting the n^th smallest positive integer that has
# exactly k ones in its binary representation. It is guaranteed that the
# answer is strictly less than 2^50.
#
# Example 1:
#
# Input: n = 4, k = 2
#
# Output: 9
#
# Explanation:
#
# The 4 smallest positive integers that have exactly k = 2 ones in their
# binary representations are:
#
# 3 = 11_2
#
# 5 = 101_2
#
# 6 = 110_2
#
# 9 = 1001_2
#
# Example 2:
#
# Input: n = 3, k = 1
#
# Output: 4
#
# Explanation:
#
# The 3 smallest positive integers that have exactly k = 1 one in their
# binary representations are:
#
# 1 = 1_2
#
# 2 = 10_2
#
# 4 = 100_2
#
# Constraints:
#
# 1 <= n <= 2^50
#
# 1 <= k <= 50
#
# The answer is strictly less than 2^50.
#

# @lc code=start
from math import comb


class Solution:
    def nthSmallest(self, n: int, k: int) -> int:
        """
        Interview explanation:
        Find the n-th smallest positive integer with exactly k set bits
        (combinatorial digit DP / digit construction).

        Algorithm:
        - Build the answer from bit 49 down to 0.
        - If bit b is unset, there are C(b, remaining) numbers; if n exceeds that,
          set bit b, subtract that count, and decrement remaining ones.

        Complexity: O(B) time with B≤50 (comb is O(1) for small args), O(1) space.
        """
        ans = 0
        remaining = k

        for bit in range(49, -1, -1):
            count_with_zero = comb(bit, remaining)

            if n > count_with_zero:
                n -= count_with_zero
                ans |= 1 << bit
                remaining -= 1
                if remaining == 0:
                    break

        return ans
# @lc code=end
