#
# @lc app=leetcode id=3145 lang=python3
#
# [3145] Find Products of Elements of Big Array
#
# https://leetcode.com/problems/find-products-of-elements-of-big-array/description/
#
# algorithms
# Hard (25.31%)
# Likes:    63
# Dislikes: 18
# Total Accepted:    3.3K
# Total Submissions: 13.1K
# Testcase Example:  "[[1,3,7]]"
#
#
# The powerful array of a non-negative integer x is defined as the
# shortest sorted array of powers of two that sum up to x. The table below
# illustrates examples of how the powerful array is determined. It can be
# proven that the powerful array of x is unique.
#
#                         num
#                         Binary Representation
#                         powerful array
#
#                         1
#                         00001
#                         [1]
#
#                         8
#                         01000
#                         [8]
#
#                         10
#                         01010
#                         [2, 8]
#
#                         13
#                         01101
#                         [1, 4, 8]
#
#                         23
#                         10111
#                         [1, 2, 4, 16]
#
# The array big_nums is created by concatenating the powerful arrays for
# every positive integer i in ascending order: 1, 2, 3, and so on. Thus,
# big_nums begins as [1, 2, 1, 2, 4, 1, 4, 2, 4, 1, 2, 4, 8, ...].
#
# You are given a 2D integer matrix queries, where for queries[i] =
# [from_i, to_i, mod_i] you should calculate (big_nums[from_i] *
# big_nums[from_i + 1] * ... * big_nums[to_i]) % mod_i.
#
# Return an integer array answer such that answer[i] is the answer to the
# i^th query.
#
# Example 1:
#
# Input: queries = [[1,3,7]]
#
# Output: [4]
#
# Explanation:
#
# There is one query.
#
# big_nums[1..3] = [2,1,2]. The product of them is 4. The result is 4 % 7
# = 4.
#
# Example 2:
#
# Input: queries = [[2,5,3],[7,7,4]]
#
# Output: [2,2]
#
# Explanation:
#
# There are two queries.
#
# First query: big_nums[2..5] = [1,2,4,1]. The product of them is 8. The
# result is 8 % 3 = 2.
#
# Second query: big_nums[7] = 2. The result is 2 % 4 = 2.
#
# Constraints:
#
# 1 <= queries.length <= 500
#
# queries[i].length == 3
#
# 0 <= queries[i][0] <= queries[i][1] <= 10^15
#
# 1 <= queries[i][2] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def findProductsOfElements(self, queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        big_nums concatenates each positive integer's set bits as powers of two
        (low to high). Range products are 2^(sum of those bit positions) mod m.

        Algorithm:
        - Bit-count formulas: total set bits / sum of bit indices in [0, n).
        - Binary-search the largest value whose powerful-array prefix fits a
          length; finish remaining bits of the next integer.
        - Query [L,R] => pow(2, prefix_exp(R+1) - prefix_exp(L), mod).

        Complexity: O(Q * B * log I) time with B≈60, I≤10^15; O(1) space.
        """

        def popcount_sum(n: int) -> int:
            """Set-bit count over integers in [0, n)."""
            if n <= 0:
                return 0
            res = 0
            for b in range(60):
                cycle = 1 << (b + 1)
                full = n // cycle
                res += full * (1 << b)
                rem = n % cycle
                res += max(0, rem - (1 << b))
            return res

        def exponent_sum(n: int) -> int:
            """Sum of set-bit positions over integers in [0, n)."""
            if n <= 0:
                return 0
            res = 0
            for b in range(60):
                cycle = 1 << (b + 1)
                full = n // cycle
                cnt = full * (1 << b) + max(0, n % cycle - (1 << b))
                res += cnt * b
            return res

        def sum_exp_prefix(count: int) -> int:
            """Sum of bit positions of the first `count` big_nums entries."""
            if count <= 0:
                return 0
            lo, hi = 0, count
            while lo < hi:
                mid = (lo + hi + 1) // 2
                if popcount_sum(mid + 1) <= count:
                    lo = mid
                else:
                    hi = mid - 1
            n = lo
            used = popcount_sum(n + 1)
            res = exponent_sum(n + 1)
            remain = count - used
            x = n + 1
            b = 0
            while remain > 0:
                if x & (1 << b):
                    res += b
                    remain -= 1
                b += 1
            return res

        ans = []
        for left, right, mod in queries:
            exp = sum_exp_prefix(right + 1) - sum_exp_prefix(left)
            ans.append(pow(2, exp, mod))
        return ans
# @lc code=end
