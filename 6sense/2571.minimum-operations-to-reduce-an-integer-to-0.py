#
# @lc app=leetcode id=2571 lang=python3
#
# [2571] Minimum Operations to Reduce an Integer to 0
#
# https://leetcode.com/problems/minimum-operations-to-reduce-an-integer-to-0/description/
#
# algorithms
# Medium (63.06%)
# Likes:    649
# Dislikes: 201
# Total Accepted:    61.1K
# Total Submissions: 96.8K
# Testcase Example:  "39"
#
# You are given a positive integer n, you can do the following operation any
# number of times:
#
#
# Add or subtract a power of 2 from n.
#
# Return the minimum number of operations to make n equal to 0.
#
# A number x is power of 2 if x == 2^i where i >= 0.
#
#
#
# Example 1:
#
# Input: n = 39
# Output: 3
# Explanation: We can do the following operations:
# - Add 2^0 = 1 to n, so now n = 40.
# - Subtract 2^3 = 8 from n, so now n = 32.
# - Subtract 2^5 = 32 from n, so now n = 0.
# It can be shown that 3 is the minimum number of operations we need to make n
# equal to 0.
#
# Example 2:
#
# Input: n = 54
# Output: 3
# Explanation: We can do the following operations:
# - Add 2^1 = 2 to n, so now n = 56.
# - Add 2^3 = 8 to n, so now n = 64.
# - Subtract 2^6 = 64 from n, so now n = 0.
# So the minimum number of operations is 3.
#
#
#
# Constraints:
#
#
# 1 <= n <= 10^5
#

# @lc code=start
class Solution:
    def minOperations(self, n: int) -> int:
        """
        Interview explanation:
        Add or subtract a power of 2 each operation to reach 0; minimize operations.
        Collapse runs of consecutive 1-bits by adding one when low bits are ...11.

        Algorithm:
        - While n>0: if n%4==3 then n+=1 (one op); else count LSB and shift.

        Complexity: O(log n) time, O(1) space.
        """
        ans = 0
        while n:
            if n & 3 == 3:
                n += 1
                ans += 1
            else:
                ans += n & 1
                n >>= 1
        return ans
# @lc code=end
