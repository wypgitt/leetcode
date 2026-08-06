#
# @lc app=leetcode id=3215 lang=python3
#
# [3215] Count Triplets with Even XOR Set Bits II
#
# https://leetcode.com/problems/count-triplets-with-even-xor-set-bits-ii/description/
#
# algorithms
# Medium (61.96%)
# Likes:    17
# Dislikes: 3
# Total Accepted:    868
# Total Submissions: 1.4K
# Testcase Example:  "[1]\n[2]\n[3]"
#
#
# Given three integer arrays a, b, and c, return the number of triplets
# (a[i], b[j], c[k]), such that the bitwise XOR between the elements of
# each triplet has an even number of set bits.
#
# Example 1:
#
# Input: a = [1], b = [2], c = [3]
#
# Output: 1
#
# Explanation:
#
# The only triplet is (a[0], b[0], c[0]) and their XOR is: 1 XOR 2 XOR 3 =
# 00_2.
#
# Example 2:
#
# Input: a = [1,1], b = [2,3], c = [1,5]
#
# Output: 4
#
# Explanation:
#
# Consider these four triplets:
#
# (a[0], b[1], c[0]): 1 XOR 3 XOR 1 = 011_2
#
# (a[1], b[1], c[0]): 1 XOR 3 XOR 1 = 011_2
#
# (a[0], b[0], c[1]): 1 XOR 2 XOR 5 = 110_2
#
# (a[1], b[0], c[1]): 1 XOR 2 XOR 5 = 110_2
#
# Constraints:
#
# 1 <= a.length, b.length, c.length <= 10^5
#
# 0 <= a[i], b[i], c[i] <= 10^9
#

# @lc code=start
from typing import List, Tuple


class Solution:
    def tripletCount(self, a: List[int], b: List[int], c: List[int]) -> int:
        """
        Interview explanation:
        popcount(x^y^z) is even iff the parity of popcount(x)+popcount(y)+popcount(z)
        is even (XOR parity equals sum of popcount parities mod 2).

        Algorithm:
        - Count even/odd popcount in each array.
        - Even total parity: EEE + EOO + OEO + OOE.

        Complexity: O(n) time, O(1) space.
        """
        def parity_counts(arr: List[int]) -> Tuple[int, int]:
            even = odd = 0
            for x in arr:
                if x.bit_count() & 1:
                    odd += 1
                else:
                    even += 1
            return even, odd

        ae, ao = parity_counts(a)
        be, bo = parity_counts(b)
        ce, co = parity_counts(c)
        return ae * be * ce + ae * bo * co + ao * be * co + ao * bo * ce
# @lc code=end
