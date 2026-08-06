#
# @lc app=leetcode id=2156 lang=python3
#
# [2156] Find Substring With Given Hash Value
#
# https://leetcode.com/problems/find-substring-with-given-hash-value/description/
#
# algorithms
# Hard (26.73%)
# Likes:    449
# Dislikes: 386
# Total Accepted:    17.6K
# Total Submissions: 65.8K
# Testcase Example:  "\"leetcode\"\n7\n20\n2\n0"
#
# The hash of a 0-indexed string s of length k, given integers p and m, is
# computed using the following function:
#
#
# hash(s, p, m) = (val(s[0]) * p^0 + val(s[1]) * p^1 + ... + val(s[k-1]) *
# p^k-1) mod m.
#
# Where val(s[i]) represents the index of s[i] in the alphabet from val('a') = 1
# to val('z') = 26.
#
# You are given a string s and the integers power, modulo, k, and hashValue.
# Return sub, the first substring of s of length k such that hash(sub, power,
# modulo) == hashValue.
#
# The test cases will be generated such that an answer always exists.
#
# A substring is a contiguous non-empty sequence of characters within a string.
#
#
#
# Example 1:
#
# Input: s = "leetcode", power = 7, modulo = 20, k = 2, hashValue = 0
# Output: "ee"
# Explanation: The hash of "ee" can be computed to be hash("ee", 7, 20) = (5 * 1
# + 5 * 7) mod 20 = 40 mod 20 = 0.
# "ee" is the first substring of length 2 with hashValue 0. Hence, we return
# "ee".
#
# Example 2:
#
# Input: s = "fbxzaad", power = 31, modulo = 100, k = 3, hashValue = 32
# Output: "fbx"
# Explanation: The hash of "fbx" can be computed to be hash("fbx", 31, 100) = (6
# * 1 + 2 * 31 + 24 * 31^2) mod 100 = 23132 mod 100 = 32.
# The hash of "bxz" can be computed to be hash("bxz", 31, 100) = (2 * 1 + 24 *
# 31 + 26 * 31^2) mod 100 = 25732 mod 100 = 32.
# "fbx" is the first substring of length 3 with hashValue 32. Hence, we return
# "fbx".
# Note that "bxz" also has a hash of 32 but it appears later than "fbx".
#
#
#
# Constraints:
#
#
# 1 <= k <= s.length <= 2 * 10^4
#
#
# 1 <= power, modulo <= 10^9
#
#
# 0 <= hashValue < modulo
#
#
# s consists of lowercase English letters only.
#
#
# The test cases are generated such that an answer always exists.
#

# @lc code=start
class Solution:
    def subStrHash(self, s: str, power: int, modulo: int, k: int, hashValue: int) -> str:
        """
        Interview explanation:
        Hash of substring s[i..i+k) is sum (val(s[i+j]) * power^j) mod modulo,
        val('a')=1..'z'=26. Find the first (smallest i) substring with given
        hashValue. Compute rolling hash from the right to avoid modular inverse.

        Algorithm:
        (rolling hash right-to-left)
        - Start at end: compute hash of s[n-k..n); slide left: remove last char
          contribution, divide-by-power effect via multiply by power after
          subtracting, add new front.
        - Track leftmost index whose hash equals hashValue.

        Complexity: O(n) time, O(1) extra space.
        """
        n = len(s)
        pk = pow(power, k, modulo)
        h = 0
        ans = 0
        for i in range(n - 1, n - k - 1, -1):
            h = (h * power + (ord(s[i]) - 96)) % modulo
        if h == hashValue:
            ans = n - k
        for i in range(n - k - 1, -1, -1):
            h = (h * power + (ord(s[i]) - 96) - (ord(s[i + k]) - 96) * pk) % modulo
            if h == hashValue:
                ans = i
        return s[ans : ans + k]
# @lc code=end
