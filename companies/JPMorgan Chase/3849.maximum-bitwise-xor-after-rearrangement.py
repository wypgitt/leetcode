#
# @lc app=leetcode id=3849 lang=python3
#
# [3849] Maximum Bitwise XOR After Rearrangement
#
# https://leetcode.com/problems/maximum-bitwise-xor-after-rearrangement/description/
#
# algorithms
# Medium (71.52%)
# Likes:    50
# Dislikes: 2
# Total Accepted:    34.1K
# Total Submissions: 47.7K
# Testcase Example:  "\"101\"\n\"011\""
#
#
# You are given two binary strings s and t​​​​​​​, each of length n.
#
# You may rearrange the characters of t in any order, but s must remain
# unchanged.
#
# Return a binary string of length n representing the maximum integer
# value obtainable by taking the bitwise XOR of s and rearranged t.
#
# Example 1:
#
# Input: s = "101", t = "011"
#
# Output: "110"
#
# Explanation:
#
# One optimal rearrangement of t is "011".
#
# The bitwise XOR of s and rearranged t is "101" XOR "011" = "110", which
# is the maximum possible.
#
# Example 2:
#
# Input: s = "0110", t = "1110"
#
# Output: "1101"
#
# Explanation:
#
# One optimal rearrangement of t is "1011".
#
# The bitwise XOR of s and rearranged t is "0110" XOR "1011" = "1101",
# which is the maximum possible.
#
# Example 3:
#
# Input: s = "0101", t = "1001"
#
# Output: "1111"
#
# Explanation:
#
# One optimal rearrangement of t is "1010".
#
# The bitwise XOR of s and rearranged t is "0101" XOR "1010" = "1111",
# which is the maximum possible.
#
# Constraints:
#
# 1 <= n == s.length == t.length <= 2 * 10^5
#
# s[i] and t[i] are either '0' or '1'.
#

# @lc code=start
class Solution:
    def maximumXor(self, s: str, t: str) -> str:
        """
        Interview explanation:
        Rearrange t to maximize the binary value of s XOR t. Prefer a 1 bit
        at each position from MSB to LSB.

        Algorithm:
        - Count 0/1 in t.
        - For each bit of s, spend the opposite bit from t if available
          (XOR=1); else spend the same bit (XOR=0).

        Complexity: O(n) time, O(n) space for the answer.
        """
        cnt = [0, 0]
        for c in t:
            cnt[int(c)] += 1
        ans = ["0"] * len(s)
        for i, c in enumerate(s):
            x = int(c)
            if cnt[x ^ 1]:
                cnt[x ^ 1] -= 1
                ans[i] = "1"
            else:
                cnt[x] -= 1
        return "".join(ans)
# @lc code=end
