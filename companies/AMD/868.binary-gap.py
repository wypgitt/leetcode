#
# @lc app=leetcode id=868 lang=python3
#
# [868] Binary Gap
#
# https://leetcode.com/problems/binary-gap/description/
#
# algorithms
# Easy (74.38%)
# Likes:    985
# Dislikes: 743
# Total Accepted:    221K
# Total Submissions: 298K
# Testcase Example:  "22"
#
# Given a positive integer n, find and return the longest distance between any
# two adjacent 1's in the binary representation of n. If there are no two
# adjacent 1's, return 0.
#
# Two 1's are adjacent if there are only 0's separating them (possibly no 0's).
# The distance between two 1's is the absolute difference between their bit
# positions. For example, the two 1's in "1001" have a distance of 3.
#
# Example 1:
#
# Input: n = 22
# Output: 2
# Explanation: 22 in binary is "10110".
# The first adjacent pair of 1's is "10110" with a distance of 2.
# The second adjacent pair of 1's is "10110" with a distance of 1.
# The answer is the largest of these two distances, which is 2.
# Note that "10110" is not a valid pair since there is a 1 separating the two
# 1's underlined.
#
# Example 2:
#
# Input: n = 8
# Output: 0
# Explanation: 8 in binary is "1000".
# There are not any adjacent pairs of 1's in the binary representation of 8, so
# we return 0.
#
# Example 3:
#
# Input: n = 5
# Output: 2
# Explanation: 5 in binary is "101".
#
# Constraints:
#
# 1 <= n <= 10^9
#

# @lc code=start
class Solution:
    def binaryGap(self, n: int) -> int:
        """
        Interview explanation:
        Largest distance between consecutive 1-bits in binary of n. Scan bits
        tracking previous 1 index.

        Algorithm:
        - For each bit position with 1, update ans with pos-prev; set prev=pos.

        Complexity: O(log n) time, O(1) space.
        """
        ans = 0
        prev = -1
        pos = 0
        while n:
            if n & 1:
                if prev != -1:
                    ans = max(ans, pos - prev)
                prev = pos
            n >>= 1
            pos += 1
        return ans

    def binaryGap_bin(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: convert to binary string and scan '1' indices.

        Algorithm:
        - Find all indices of '1' in bin(n)[2:]; max consecutive gap.

        Complexity: O(log n) time, O(log n) space.
        """
        s = bin(n)[2:]
        prev = -1
        ans = 0
        for i, ch in enumerate(s):
            if ch == "1":
                if prev != -1:
                    ans = max(ans, i - prev)
                prev = i
        return ans
# @lc code=end

