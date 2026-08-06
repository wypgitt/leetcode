#
# @lc app=leetcode id=3199 lang=python3
#
# [3199] Count Triplets with Even XOR Set Bits I
#
# https://leetcode.com/problems/count-triplets-with-even-xor-set-bits-i/description/
#
# algorithms
# Easy (83.02%)
# Likes:    9
# Dislikes: 4
# Total Accepted:    2K
# Total Submissions: 2.4K
# Testcase Example:  "[1]\n[2]\n[3]"
#
#
# Given three integer arrays a, b, and c, return the number of triplets
# (a[i], b[j], c[k]), such that the bitwise XOR of the elements of each
# triplet has an even number of set bits.
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
# 1 <= a.length, b.length, c.length <= 100
#
# 0 <= a[i], b[i], c[i] <= 100
#

# @lc code=start

from typing import List


class Solution:
    def tripletCount(self, a: List[int], b: List[int], c: List[int]) -> int:
        """
        Interview explanation:
        Count triplets whose XOR has even popcount. popcount(x^y^z) is even iff
        the XOR of the three popcount-parities is 0 (even number of odds).

        Algorithm:
        - Brute triple loop (lengths <= 100); check bin(x^y^z).count('1') % 2 == 0.

        Complexity: O(|a|*|b|*|c|) time, O(1) space.
        """
        ans = 0
        for x in a:
            for y in b:
                for z in c:
                    if (x ^ y ^ z).bit_count() % 2 == 0:
                        ans += 1
        return ans

    def tripletCount_parity(self, a: List[int], b: List[int], c: List[int]) -> int:
        """
        Interview explanation:
        Parity counting: even XOR-popcount iff #odd-popcount among (a,b,c) is even.

        Algorithm:
        - Count even/odd popcounts in each array; sum products for (EEE, EOO, OEO, OOE).

        Complexity: O(|a|+|b|+|c|) time, O(1) space.
        """
        def eo(arr: List[int]):
            e = o = 0
            for x in arr:
                if x.bit_count() & 1:
                    o += 1
                else:
                    e += 1
            return e, o

        ae, ao = eo(a)
        be, bo = eo(b)
        ce, co = eo(c)
        return ae * be * ce + ae * bo * co + ao * be * co + ao * bo * ce
# @lc code=end
