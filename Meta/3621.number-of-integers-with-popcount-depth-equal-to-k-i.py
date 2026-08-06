#
# @lc app=leetcode id=3621 lang=python3
#
# [3621] Number of Integers With Popcount-Depth Equal to K I
#
# https://leetcode.com/problems/number-of-integers-with-popcount-depth-equal-to-k-i/description/
#
# algorithms
# Hard (23.29%)
# Likes:    55
# Dislikes: 5
# Total Accepted:    4.9K
# Total Submissions: 21.2K
# Testcase Example:  "4\n1"
#
#
# You are given two integers n and k.
#
# For any positive integer x, define the following sequence:
#
# p_0 = x
#
# p_i+1 = popcount(p_i) for all i >= 0, where popcount(y) is the number of
# set bits (1's) in the binary representation of y.
#
# This sequence will eventually reach the value 1.
#
# The popcount-depth of x is defined as the smallest integer d >= 0 such
# that p_d = 1.
#
# For example, if x = 7 (binary representation "111"). Then, the sequence
# is: 7 → 3 → 2 → 1, so the popcount-depth of 7 is 3.
#
# Your task is to determine the number of integers in the range [1, n]
# whose popcount-depth is exactly equal to k.
#
# Return the number of such integers.
#
# Example 1:
#
# Input: n = 4, k = 1
#
# Output: 2
#
# Explanation:
#
# The following integers in the range [1, 4] have popcount-depth exactly
# equal to 1:
#
#                         x
#                         Binary
#                         Sequence
#
#                         2
#                         "10"
#                         2 → 1
#
#                         4
#                         "100"
#                         4 → 1
#
# Thus, the answer is 2.
#
# Example 2:
#
# Input: n = 7, k = 2
#
# Output: 3
#
# Explanation:
#
# The following integers in the range [1, 7] have popcount-depth exactly
# equal to 2:
#
#                         x
#                         Binary
#                         Sequence
#
#                         3
#                         "11"
#                         3 → 2 → 1
#
#                         5
#                         "101"
#                         5 → 2 → 1
#
#                         6
#                         "110"
#                         6 → 2 → 1
#
# Thus, the answer is 3.
#
# Constraints:
#
# 1 <= n <= 10^15
#
# 0 <= k <= 5
#

# @lc code=start

class Solution:
    def popcountDepth(self, n: int, k: int) -> int:
        """
        Interview explanation:
        Popcount-depth of x is steps of x -> popcount(x) until 1. For n up to
        1e15, count how many x in [1, n] have depth exactly k via combinatorics
        on bit counts: depth(x)=0 only for 1; depth=1 for powers of two; for
        k>=2, x with popcount c has depth 1+depth(c).

        Algorithm:
        - Precompute C(i, j) and depth D[c] for c up to bit length.
        - k==0 -> 1; k==1 -> floor(log2(n)).
        - Else sum count_leq(n, c) over c with D[c]==k-1, where count_leq
          walks bits of n and adds C(lower_bits, remaining_ones).

        Complexity: O((log n)^2) time and space (precompute once).
        """
        def count_with_ones(c: int) -> int:
            result = ones = 0
            for i in range(n.bit_length() - 1, -1, -1):
                if not (n & (1 << i)):
                    continue
                need = c - ones
                if 0 <= need <= i:
                    result += self._NCR[i][need]
                ones += 1
            if ones == c:
                result += 1
            return result

        if k == 0:
            return 1
        if k == 1:
            return n.bit_length() - 1
        return sum(
            count_with_ones(c)
            for c in range(2, n.bit_length() + 1)
            if self._D[c] == k - 1
        )


def _init_popcount_tables():
    max_bits = (10**15).bit_length()
    ncr = [[0] * (max_bits + 1) for _ in range(max_bits + 1)]
    for i in range(max_bits + 1):
        for j in range(i + 1):
            ncr[i][j] = 1 if j == 0 or j == i else ncr[i - 1][j] + ncr[i - 1][j - 1]
    depth = [0] * (max_bits + 1)
    for i in range(2, max_bits + 1):
        depth[i] = depth[bin(i).count("1")] + 1
    return ncr, depth


Solution._NCR, Solution._D = _init_popcount_tables()
# @lc code=end

