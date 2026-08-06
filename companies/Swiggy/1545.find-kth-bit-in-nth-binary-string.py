#
# @lc app=leetcode id=1545 lang=python3
#
# [1545] Find Kth Bit in Nth Binary String
#
# https://leetcode.com/problems/find-kth-bit-in-nth-binary-string/description/
#
# algorithms
# Medium (73.72%)
# Likes:    1882
# Dislikes: 123
# Total Accepted:    287K
# Total Submissions: 390K
# Testcase Example:  "3"
#
# Given two positive integers n and k, the binary string S_n is formed as
# follows:
#
# S_1 = "0"
#
# S_i = S_i - 1 + "1" + reverse(invert(S_i - 1)) for i > 1
#
# Where + denotes the concatenation operation, reverse(x) returns the reversed
# string x, and invert(x) inverts all the bits in x (0 changes to 1 and 1
# changes to 0).
#
# For example, the first four strings in the above sequence are:
#
# S_1 = "0"
#
# S_2 = "011"
#
# S_3 = "0111001"
#
# S_4 = "011100110110001"
#
# Return the k^th bit in S_n. It is guaranteed that k is valid for the given n.
#
# Example 1:
#
# Input: n = 3, k = 1
# Output: "0"
# Explanation: S_3 is "0111001".
# The 1^st bit is "0".
#
# Example 2:
#
# Input: n = 4, k = 11
# Output: "1"
# Explanation: S_4 is "011100110110001".
# The 11^th bit is "1".
#
# Constraints:
#
# 1 <= n <= 20
#
# 1 <= k <= 2^n - 1
#

# @lc code=start
class Solution:
    def findKthBit(self, n: int, k: int) -> str:
        """
        Interview explanation:
        S1="0"; Si = Si-1 + "1" + reverse(invert(Si-1)). Length = 2^n - 1.
        Recurse: mid = 2^{n-1}; if k==mid return '1'; if k<mid recurse left;
        else invert of bit at (mid - (k-mid)) in S_{n-1}.

        Algorithm:
        - Recursive (or iterative) locate without building the string.

        Complexity: O(n) time, O(n) recursion space.
        """
        if n == 1:
            return "0"
        mid = 1 << (n - 1)  # 2^{n-1}
        if k == mid:
            return "1"
        if k < mid:
            return self.findKthBit(n - 1, k)
        # mirrored position in left half
        bit = self.findKthBit(n - 1, mid - (k - mid))
        return "0" if bit == "1" else "1"

    def findKthBit_build(self, n: int, k: int) -> str:
        """
        Interview explanation:
        Alternate: explicitly build Sn (length 2^n-1 <= 1023 for n<=20) and index.

        Algorithm:
        - Iteratively expand string n times; return s[k-1].

        Complexity: O(2^n) time/space.
        """
        s = "0"
        for _ in range(n - 1):
            inv = "".join("1" if c == "0" else "0" for c in s)
            s = s + "1" + inv[::-1]
        return s[k - 1]
# @lc code=end
