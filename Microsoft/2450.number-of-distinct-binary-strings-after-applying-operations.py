#
# @lc app=leetcode id=2450 lang=python3
#
# [2450] Number of Distinct Binary Strings After Applying Operations
#
# https://leetcode.com/problems/number-of-distinct-binary-strings-after-applying-operations/description/
#
# algorithms
# Medium (63.06%)
# Likes:    39
# Dislikes: 9
# Total Accepted:    1.4K
# Total Submissions: 2.2K
# Testcase Example:  "\"1001\"\n3"
#
#
# You are given a binary string s and a positive integer k.
#
# You can apply the following operation on the string any number of times:
#
# Choose any substring of size k from s and flip all its characters, that
# is, turn all 1's into 0's, and all 0's into 1's.
#
# Return the number of distinct strings you can obtain. Since the answer
# may be too large, return it modulo 10^9 + 7.
#
# Note that:
#
# A binary string is a string that consists only of the characters 0 and
# 1.
#
# A substring is a contiguous part of a string.
#
# Example 1:
#
# Input: s = "1001", k = 3
# Output: 4
# Explanation: We can obtain the following strings:
# - Applying no operation on the string gives s = "1001".
# - Applying one operation on the substring starting at index 0 gives s =
# "0111".
# - Applying one operation on the substring starting at index 1 gives s =
# "1110".
# - Applying one operation on both the substrings starting at indices 0
# and 1 gives s = "0000".
# It can be shown that we cannot obtain any other string, so the answer is
# 4.
#
# Example 2:
#
# Input: s = "10110", k = 5
# Output: 2
# Explanation: We can obtain the following strings:
# - Applying no operation on the string gives s = "10110".
# - Applying one operation on the whole string gives s = "01001".
# It can be shown that we cannot obtain any other string, so the answer is
# 2.
#
# Constraints:
#
# 1 <= k <= s.length <= 10^5
#
# s[i] is either 0 or 1.
#
# @lc code=start
class Solution:
    def countDistinctStrings(self, s: str, k: int) -> int:
        """
        Interview explanation:
        Premium. Flip any length-k substring any times; count distinct reachable
        binary strings mod 1e9+7.

        Algorithm:
        - Operations span a space of dimension n-k+1; answer 2^(n-k+1) mod MOD.

        Complexity: O(log (n-k)) via fast pow, O(1) space.
        """
        MOD = 10**9 + 7
        return pow(2, len(s) - k + 1, MOD)

    def countDistinctStrings_math(self, s: str, k: int) -> int:
        """
        Interview explanation:
        Alternate same closed form.

        Algorithm:
        - Modular exponentiation of 2^(n-k+1).

        Complexity: O(log n) time, O(1) space.
        """
        return self.countDistinctStrings(s, k)
# @lc code=end
