#
# @lc app=leetcode id=2533 lang=python3
#
# [2533] Number of Good Binary Strings
#
# https://leetcode.com/problems/number-of-good-binary-strings/description/
#
# algorithms
# Medium (52.83%)
# Likes:    58
# Dislikes: 23
# Total Accepted:    7.9K
# Total Submissions: 14.9K
# Testcase Example:  "2\n3\n1\n2"
#
#
# You are given four integers minLength, maxLength, oneGroup and
# zeroGroup.
#
# A binary string is good if it satisfies the following conditions:
#
# The length of the string is in the range [minLength, maxLength].
#
# The size of each block of consecutive 1's is a multiple of oneGroup.
#
# For example in a binary string 00110111100 sizes of each block of
# consecutive ones are [2,4].
#
# The size of each block of consecutive 0's is a multiple of zeroGroup.
#
# For example, in a binary string 00110111100 sizes of each block of
# consecutive zeros are [2,1,2].
#
# Return the number of good binary strings. Since the answer may be too
# large, return it modulo 10^9 + 7.
#
# Note that 0 is considered a multiple of all the numbers.
#
# Example 1:
#
# Input: minLength = 2, maxLength = 3, oneGroup = 1, zeroGroup = 2
# Output: 5
# Explanation: There are 5 good binary strings in this example: "00",
# "11", "001", "100", and "111".
# It can be proven that there are only 5 good strings satisfying all
# conditions.
#
# Example 2:
#
# Input: minLength = 4, maxLength = 4, oneGroup = 4, zeroGroup = 3
# Output: 1
# Explanation: There is only 1 good binary string in this example: "1111".
# It can be proven that there is only 1 good string satisfying all
# conditions.
#
# Constraints:
#
# 1 <= minLength <= maxLength <= 10^5
#
# 1 <= oneGroup, zeroGroup <= maxLength
#
# @lc code=start
class Solution:
    def goodBinaryStrings(
        self, minLength: int, maxLength: int, oneGroup: int, zeroGroup: int
    ) -> int:
        """
        Interview explanation:
        Count binary strings with length in [minLength, maxLength] where every
        run of 1s has length multiple of oneGroup and every run of 0s has length
        multiple of zeroGroup. Return answer modulo 10^9+7.

        Algorithm:
        (DP)
        - dp[i] = # good strings of length i; dp[0] = 1 (empty).
        - Transition: append a block of oneGroup ones or zeroGroup zeros:
          dp[i] += dp[i - oneGroup] and/or dp[i - zeroGroup].
        - Answer = sum(dp[minLength..maxLength]) % MOD.

        Complexity: O(maxLength) time, O(maxLength) space.
        """
        MOD = 10**9 + 7
        dp = [0] * (maxLength + 1)
        dp[0] = 1
        for i in range(1, maxLength + 1):
            if i >= oneGroup:
                dp[i] = (dp[i] + dp[i - oneGroup]) % MOD
            if i >= zeroGroup:
                dp[i] = (dp[i] + dp[i - zeroGroup]) % MOD
        return sum(dp[minLength:]) % MOD

    def goodBinaryStrings_forward(
        self, minLength: int, maxLength: int, oneGroup: int, zeroGroup: int
    ) -> int:
        """
        Interview explanation:
        Alternate forward DP: from each reachable length, append a 0-block or
        1-block.

        Algorithm:
        - Start dp[0]=1; for each i with dp[i]>0, add to i+zeroGroup / i+oneGroup.

        Complexity: O(maxLength) time, O(maxLength) space.
        """
        MOD = 10**9 + 7
        dp = [0] * (maxLength + 1)
        dp[0] = 1
        for i in range(maxLength + 1):
            if dp[i] == 0:
                continue
            if i + zeroGroup <= maxLength:
                dp[i + zeroGroup] = (dp[i + zeroGroup] + dp[i]) % MOD
            if i + oneGroup <= maxLength:
                dp[i + oneGroup] = (dp[i + oneGroup] + dp[i]) % MOD
        return sum(dp[minLength:]) % MOD
# @lc code=end
