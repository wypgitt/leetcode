#
# @lc app=leetcode id=3897 lang=python3
#
# [3897] Maximum Value of Concatenated Binary Segments
#
# https://leetcode.com/problems/maximum-value-of-concatenated-binary-segments/description/
#
# algorithms
# Hard (26.61%)
# Likes:    71
# Dislikes: 3
# Total Accepted:    13.6K
# Total Submissions: 51.1K
# Testcase Example:  "[1,2]\n[1,0]"
#
#
# You are given two integer arrays nums1 and nums0, each of size n.
#
# nums1[i] represents the number of '1's in the i^th segment.
#
# nums0[i] represents the number of '0's in the i^th segment.
#
# For each index i, construct a binary segment consisting of:
#
# nums1[i] occurrences of '1' followed by
#
# nums0[i] occurrences of '0'.
#
# You may rearrange the order of these segments in any way. After
# rearranging, concatenate all segments to form a single binary string.
#
# Return the maximum possible integer value of the concatenated binary
# string.
#
# Since the result can be very large, return the answer modulo 10^9 + 7.
#
# Example 1:
#
# Input: nums1 = [1,2], nums0 = [1,0]
#
# Output: 14
#
# Explanation:
#
# At index 0, nums1[0] = 1 and nums0[0] = 1, so the segment formed is
# "10".
#
# At index 1, nums1[1] = 2 and nums0[1] = 0, so the segment formed is
# "11".
#
# Reordering the segments as "11" followed by "10" produces the binary
# string "1110".
#
# The binary number "1110" has value 14 which is the maximum possible
# value.
#
# Example 2:
#
# Input: nums1 = [3,1], nums0 = [0,3]
#
# Output: 120
#
# Explanation:
#
# At index 0, nums1[0] = 3 and nums0[0] = 0, so the segment formed is
# "111".
#
# At index 1, nums1[1] = 1 and nums0[1] = 3, so the segment formed is
# "1000".
#
# Reordering the segments as "111" followed by "1000" produces the binary
# string "1111000".
#
# The binary number "1111000" has value 120 which is the maximum possible
# value.
#
# Constraints:
#
# 1 <= n == nums1.length == nums0.length <= 10^5
#
# 0 <= nums1[i], nums0[i] <= 10^4
#
# nums1[i] + nums0[i] > 0
#
# The total sum of all elements in nums1 and nums0 does not exceed 2 *
# 10^5.
#

# @lc code=start
class Solution:
    MOD = 10**9 + 7
    MAX_TOTAL = 2 * 10**5
    _POW2 = None

    @classmethod
    def _pow2(cls):
        if cls._POW2 is None:
            p = [1] * (cls.MAX_TOTAL + 1)
            for i in range(cls.MAX_TOTAL):
                p[i + 1] = (p[i] * 2) % cls.MOD
            cls._POW2 = p
        return cls._POW2

    def maxValue(self, nums1: list[int], nums0: list[int]) -> int:
        """
        Interview explanation:
        Each segment is 1^a 0^b. To maximize the binary value, place all-ones
        segments first, then order mixed segments by preferring more leading 1s
        (sort by (-ones, zeros)).

        Algorithm:
        - Start with value of concatenated pure-1 segments: 2^{total1}-1.
        - Append each mixed segment: val = val * 2^{a+b} + (2^a - 1) * 2^b.

        Complexity: O(n log n) time, O(n + L) space for pow2 table.
        """
        MOD = self.MOD
        POW2 = self._pow2()
        pure1 = sum(a for a, b in zip(nums1, nums0) if b == 0)
        segments = [(a, b) for a, b in zip(nums1, nums0) if b]
        segments.sort(key=lambda x: (-x[0], x[1]))
        result = (POW2[pure1] - 1) % MOD
        for a, b in segments:
            result = (result * POW2[a + b] + (POW2[a] - 1) * POW2[b]) % MOD
        return result
# @lc code=end
