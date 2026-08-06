#
# @lc app=leetcode id=2081 lang=python3
#
# [2081] Sum of k-Mirror Numbers
#
# https://leetcode.com/problems/sum-of-k-mirror-numbers/description/
#
# algorithms
# Hard (63.55%)
# Likes:    435
# Dislikes: 210
# Total Accepted:    78.1K
# Total Submissions: 122.8K
# Testcase Example:  "2\n5"
#
# A k-mirror number is a positive integer without leading zeros that reads the
# same both forward and backward in base-10 as well as in base-k.
#
#
# For example, 9 is a 2-mirror number. The representation of 9 in base-10 and
# base-2 are 9 and 1001 respectively, which read the same both forward and
# backward.
#
#
# On the contrary, 4 is not a 2-mirror number. The representation of 4 in base-2
# is 100, which does not read the same both forward and backward.
#
# Given the base k and the number n, return the sum of the n smallest k-mirror
# numbers.
#
#
#
# Example 1:
#
# Input: k = 2, n = 5
# Output: 25
# Explanation:
# The 5 smallest 2-mirror numbers and their representations in base-2 are listed
# as follows:
#   base-10    base-2
#     1          1
#     3          11
#     5          101
#     7          111
#     9          1001
# Their sum = 1 + 3 + 5 + 7 + 9 = 25.
#
# Example 2:
#
# Input: k = 3, n = 7
# Output: 499
# Explanation:
# The 7 smallest 3-mirror numbers are and their representations in base-3 are
# listed as follows:
#   base-10    base-3
#     1          1
#     2          2
#     4          11
#     8          22
#     121        11111
#     151        12121
#     212        21212
# Their sum = 1 + 2 + 4 + 8 + 121 + 151 + 212 = 499.
#
# Example 3:
#
# Input: k = 7, n = 17
# Output: 20379000
# Explanation: The 17 smallest 7-mirror numbers are:
# 1, 2, 3, 4, 5, 6, 8, 121, 171, 242, 292, 16561, 65656, 2137312, 4602064,
# 6597956, 6958596
#
#
#
# Constraints:
#
#
# 2 <= k <= 9
#
#
# 1 <= n <= 30
#

# @lc code=start
class Solution:
    def kMirror(self, k: int, n: int) -> int:
        """
        Interview explanation:
        Sum the n smallest positive integers that are palindromes in both
        base 10 and base k.

        Algorithm:
        - Generate base-10 palindromes in increasing order by mirroring a half
          integer (odd/even lengths). Accept if also a base-k palindrome.

        Complexity: O(P * log P) where P is palindromes scanned until n found.
        """
        def is_pal_base(x: int, base: int) -> bool:
            digits = []
            while x:
                digits.append(x % base)
                x //= base
            return digits == digits[::-1]

        total = cnt = 0
        length = 1
        while cnt < n:
            half_len = (length + 1) // 2
            start = 10 ** (half_len - 1) if half_len > 1 else 1
            end = 10 ** half_len
            for half in range(start, end):
                s = str(half)
                if length % 2 == 1:
                    pal = int(s + s[-2::-1])
                else:
                    pal = int(s + s[::-1])
                if is_pal_base(pal, k):
                    total += pal
                    cnt += 1
                    if cnt == n:
                        return total
            length += 1
        return total
# @lc code=end
