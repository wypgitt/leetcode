#
# @lc app=leetcode id=3950 lang=python3
#
# [3950] Exactly One Consecutive Set Bits Pair
#
# https://leetcode.com/problems/exactly-one-consecutive-set-bits-pair/description/
#
# algorithms
# Easy (50.91%)
# Likes:    31
# Dislikes: 10
# Total Accepted:    39.6K
# Total Submissions: 77.8K
# Testcase Example:  "6"
#
#
# You are given an integer n.
#
# Return true if its binary representation contains exactly one adjacent
# pair of set bits, and false otherwise.
#
# Example 1:
#
# Input: n = 6
#
# Output: true
#
# Explanation:
#
# Binary representation of 6 is 110.
#
# There is exactly one adjacent pair of set bits ("11"). Thus, the answer
# is true​​​​​​​.
#
# Example 2:
#
# Input: n = 5
#
# Output: false
#
# Explanation:
#
# Binary representation of 5 is 101.
#
# There is no adjacent pair of set bits. Thus, the answer is false​​​​​​​.
#
# Constraints:
#
# 0 <= n <= 10^5
#

# @lc code=start
class Solution:
    def consecutiveSetBits(self, n: int) -> bool:
        """
        Interview explanation:
        Count adjacent set-bit pairs via n & (n>>1); need exactly one.

        Algorithm:
        - Return popcount(n & (n >> 1)) == 1.

        Complexity: O(1) / O(log n) bit ops.
        """
        return bin(n & (n >> 1)).count("1") == 1

    def consecutiveSetBits_scan(self, n: int) -> bool:
        """
        Interview explanation:
        Alternate: walk bits and count adjacent set pairs.

        Algorithm:
        - While n: if low two bits are 11, increment; shift by 1.

        Complexity: O(log n).
        """
        pairs = 0
        x = n
        while x:
            if (x & 3) == 3:
                pairs += 1
            x >>= 1
        return pairs == 1
# @lc code=end
