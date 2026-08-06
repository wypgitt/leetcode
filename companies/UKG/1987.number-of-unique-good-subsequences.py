#
# @lc app=leetcode id=1987 lang=python3
#
# [1987] Number of Unique Good Subsequences
#
# https://leetcode.com/problems/number-of-unique-good-subsequences/description/
#
# algorithms
# Hard (52.51%)
# Likes:    757
# Dislikes: 17
# Total Accepted:    17.7K
# Total Submissions: 33.7K
# Testcase Example:  "\"001\""
#
# You are given a binary string binary. A subsequence of binary is considered
# good if it is not empty and has no leading zeros (with the exception of "0").
#
# Find the number of unique good subsequences of binary.
#
# For example, if binary = "001", then all the good subsequences are ["0", "0",
# "1"], so the unique good subsequences are "0" and "1". Note that subsequences
# "00", "01", and "001" are not good because they have leading zeros.
#
# Return the number of unique good subsequences of binary. Since the answer may
# be very large, return it modulo 10^9 + 7.
#
# A subsequence is a sequence that can be derived from another sequence by
# deleting some or no elements without changing the order of the remaining
# elements.
#
# Example 1:
#
# Input: binary = "001"
# Output: 2
# Explanation: The good subsequences of binary are ["0", "0", "1"].
# The unique good subsequences are "0" and "1".
#
# Example 2:
#
# Input: binary = "11"
# Output: 2
# Explanation: The good subsequences of binary are ["1", "1", "11"].
# The unique good subsequences are "1" and "11".
#
# Example 3:
#
# Input: binary = "101"
# Output: 5
# Explanation: The good subsequences of binary are ["1", "0", "1", "10", "11",
# "101"].
# The unique good subsequences are "0", "1", "10", "11", and "101".
#
# Constraints:
#
# 1 <= binary.length <= 10^5
#
# binary consists of only '0's and '1's.
#

# @lc code=start
class Solution:
    def numberOfUniqueGoodSubsequences(self, binary: str) -> int:
        """
        Interview explanation:
        Count distinct nonempty binary subsequences without leading zeros
        (except subsequence "0"). DP: ends0 / ends1 counts of unique good
        subsequences ending with 0/1; seen zero flag.

        Algorithm:
        - MOD; for bit: if '1': ends1 = ends0+ends1+1; else ends0 = ends0+ends1;
          has0 |= bit=='0'.
        - Answer ends0+ends1 + has0.

        Complexity: O(n) time, O(1) space.
        """
        MOD = 10**9 + 7
        ends0 = ends1 = 0
        has0 = False
        for c in binary:
            if c == "1":
                ends1 = (ends0 + ends1 + 1) % MOD
            else:
                ends0 = (ends0 + ends1) % MOD
                has0 = True
        return (ends0 + ends1 + (1 if has0 else 0)) % MOD

    def numberOfUniqueGoodSubsequences_clarity(self, binary: str) -> int:
        """
        Interview explanation:
        Alternate narration of the same DP with named variables dp0/dp1.

        Algorithm:
        - Same transitions; add 1 if a lone zero appears anywhere.

        Complexity: O(n) time, O(1) space.
        """
        MOD = 10**9 + 7
        dp0 = dp1 = 0
        zero = 0
        for c in binary:
            if c == "0":
                dp0 = (dp0 + dp1) % MOD
                zero = 1
            else:
                dp1 = (dp0 + dp1 + 1) % MOD
        return (dp0 + dp1 + zero) % MOD
# @lc code=end

