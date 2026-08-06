#
# @lc app=leetcode id=1611 lang=python3
#
# [1611] Minimum One Bit Operations to Make Integers Zero
#
# https://leetcode.com/problems/minimum-one-bit-operations-to-make-integers-zero/description/
#
# algorithms
# Hard (78.19%)
# Likes:    1226
# Dislikes: 1221
# Total Accepted:    123K
# Total Submissions: 157K
# Testcase Example:  "3"
#
# Given an integer n, you must transform it into 0 using the following
# operations any number of times:
#
# Change the rightmost (0^th) bit in the binary representation of n.
#
# Change the i^th bit in the binary representation of n if the (i-1)^th bit is
# set to 1 and the (i-2)^th through 0^th bits are set to 0.
#
# Return the minimum number of operations to transform n into 0.
#
# Example 1:
#
# Input: n = 3
# Output: 2
# Explanation: The binary representation of 3 is "11".
# "11" -> "01" with the 2^nd operation since the 0^th bit is 1.
# "01" -> "00" with the 1^st operation.
#
# Example 2:
#
# Input: n = 6
# Output: 4
# Explanation: The binary representation of 6 is "110".
# "110" -> "010" with the 2^nd operation since the 1^st bit is 1 and 0^th
# through 0^th bits are 0.
# "010" -> "011" with the 1^st operation.
# "011" -> "001" with the 2^nd operation since the 0^th bit is 1.
# "001" -> "000" with the 1^st operation.
#
# Constraints:
#
# 0 <= n <= 10^9
#

# @lc code=start
class Solution:
    def minimumOneBitOperations(self, n: int) -> int:
        """
        Interview explanation:
        Allowed ops map n to Gray-code neighbors; min ops to 0 equals the inverse
        Gray code / known recurrence for this problem.

        Algorithm (Gray-code / bit recursion):
        - Answer is n ⊕ (n>>1) ⊕ (n>>2) ⊕ ... (convert binary to Gray inverse),
          equivalently: while n: ans ^= n; n >>= 1.

        Complexity: O(log n) time, O(1) space.
        """
        ans = 0
        while n:
            ans ^= n
            n >>= 1
        return ans

    def minimumOneBitOperations_recursive(self, n: int) -> int:
        """
        Interview explanation:
        Alternate recursive view: to clear highest bit, need f(2^k-1) + 1 + f(n-2^k)
        with f(2^k-1)=2^k-1 pattern; standard textbook recurrence.

        Algorithm (recursive):
        - If n==0 return 0. Let k = msb; return (1<< (k+1)) - 1 - f(n ^ (1<<k)).

        Complexity: O(log n) time, O(log n) space.
        """
        def f(x: int) -> int:
            if x == 0:
                return 0
            k = x.bit_length() - 1
            return ((1 << (k + 1)) - 1) - f(x ^ (1 << k))

        return f(n)
# @lc code=end
