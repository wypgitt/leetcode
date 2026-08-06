#
# @lc app=leetcode id=1573 lang=python3
#
# [1573] Number of Ways to Split a String
#
# https://leetcode.com/problems/number-of-ways-to-split-a-string/description/
#
# algorithms
# Medium (34.73%)
# Likes:    772
# Dislikes: 88
# Total Accepted:    36.8K
# Total Submissions: 106K
# Testcase Example:  "\"10101\""
#
# Given a binary string s, you can split s into 3 non-empty strings s1, s2, and
# s3 where s1 + s2 + s3 = s.
#
# Return the number of ways s can be split such that the number of ones is the
# same in s1, s2, and s3. Since the answer may be too large, return it modulo
# 10^9 + 7.
#
# Example 1:
#
# Input: s = "10101"
# Output: 4
# Explanation: There are four ways to split s in 3 parts where each part
# contain the same number of letters '1'.
# "1|010|1"
# "1|01|01"
# "10|10|1"
# "10|1|01"
#
# Example 2:
#
# Input: s = "1001"
# Output: 0
#
# Example 3:
#
# Input: s = "0000"
# Output: 3
# Explanation: There are three ways to split s in 3 parts.
# "0|0|00"
# "0|00|0"
# "00|0|0"
#
# Constraints:
#
# 3 <= s.length <= 10^5
#
# s[i] is either '0' or '1'.
#

# @lc code=start
class Solution:
    def numWays(self, s: str) -> int:
        """
        Interview explanation:
        Split into 3 nonempty contiguous parts with equal number of '1's.
        If total ones not divisible by 3 → 0. If 0 ones → C(n-1, 2) ways to
        place 2 cuts. Else find gaps of zeros between the 1st/2nd third and
        2nd/3rd third of ones; multiply (gap1+1)*(gap2+1).

        Algorithm:
        - Count ones; MOD=1e9+7.
        - ones==0: return (n-1)*(n-2)//2 % MOD
        - Find positions of ones; target = ones//3.
        - ways between ones[target-1]..ones[target] and ones[2*target-1]..ones[2*target]

        Complexity: O(n) time, O(n) or O(1) space.
        """
        MOD = 10**9 + 7
        n = len(s)
        ones = s.count("1")
        if ones % 3:
            return 0
        if ones == 0:
            return (n - 1) * (n - 2) // 2 % MOD
        target = ones // 3
        first = second = 0
        cnt = 0
        # count zeros in the two split windows via scanning
        # positions of the target-th and 2*target-th ones delimit gaps
        pos = []
        for i, ch in enumerate(s):
            if ch == "1":
                pos.append(i)
        # gap after ones[target-1] before ones[target]
        first = pos[target] - pos[target - 1]
        second = pos[2 * target] - pos[2 * target - 1]
        return first * second % MOD
# @lc code=end

