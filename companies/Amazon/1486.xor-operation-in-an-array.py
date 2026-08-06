#
# @lc app=leetcode id=1486 lang=python3
#
# [1486] XOR Operation in an Array
#
# https://leetcode.com/problems/xor-operation-in-an-array/description/
#
# algorithms
# Easy (87.79%)
# Likes:    1527
# Dislikes: 341
# Total Accepted:    284K
# Total Submissions: 323K
# Testcase Example:  "5"
#
# You are given an integer n and an integer start.
#
# Define an array nums where nums[i] = start + 2 * i (0-indexed) and n ==
# nums.length.
#
# Return the bitwise XOR of all elements of nums.
#
# Example 1:
#
# Input: n = 5, start = 0
# Output: 8
# Explanation: Array nums is equal to [0, 2, 4, 6, 8] where (0 ^ 2 ^ 4 ^ 6 ^ 8)
# = 8.
# Where "^" corresponds to bitwise XOR operator.
#
# Example 2:
#
# Input: n = 4, start = 3
# Output: 8
# Explanation: Array nums is equal to [3, 5, 7, 9] where (3 ^ 5 ^ 7 ^ 9) = 8.
#
# Constraints:
#
# 1 <= n <= 1000
#
# 0 <= start <= 1000
#
# n == nums.length
#

# @lc code=start
class Solution:
    def xorOperation(self, n: int, start: int) -> int:
        """
        Interview explanation:
        XOR of nums[i] = start + 2*i for i in 0..n-1.

        Algorithm:
        - Initialize ans=0; for i in range(n): ans ^= start + 2*i.

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        for i in range(n):
            ans ^= start + 2 * i
        return ans

    def xorOperation_formula(self, n: int, start: int) -> int:
        """
        Interview explanation:
        Alternate: XOR of arithmetic progression of even numbers has a closed
        form via xor-of-0..x patterns (xor from start//2 for n terms, then <<1,
        xor start&1 if n odd).

        Algorithm:
        - Let xor_upto(x)=x^(x>>1) pattern for 0..x; compute range XOR of
          start/2 .. start/2+n-1; shift and fix LSB.

        Complexity: O(1) time/space.
        """

        def xor_0_to(x: int) -> int:
            r = x % 4
            if r == 0:
                return x
            if r == 1:
                return 1
            if r == 2:
                return x + 1
            return 0

        def xor_range(l, r):
            if l == 0:
                return xor_0_to(r)
            return xor_0_to(r) ^ xor_0_to(l - 1)

        s = start // 2
        res = xor_range(s, s + n - 1) << 1
        if n & 1:
            res ^= start & 1
        return res
# @lc code=end
