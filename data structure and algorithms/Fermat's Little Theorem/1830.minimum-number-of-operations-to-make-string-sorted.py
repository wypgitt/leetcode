#
# @lc app=leetcode id=1830 lang=python3
#
# [1830] Minimum Number of Operations to Make String Sorted
#
# https://leetcode.com/problems/minimum-number-of-operations-to-make-string-sorted/description/
#
# algorithms
# Hard (50.4%)
# Likes:    191
# Dislikes: 132
# Total Accepted:    5.9K
# Total Submissions: 11.6K
# Testcase Example:  "\"cba\""
#
# You are given a string s (0-indexed). You are asked to perform the following
# operation on s until you get a sorted string:
#
# Find the largest index i such that 1 <= i < s.length and s[i] < s[i - 1].
#
# Find the largest index j such that i <= j < s.length and s[k] < s[i - 1] for
# all the possible values of k in the range [i, j] inclusive.
#
# Swap the two characters at indices i - 1 and j.
#
# Reverse the suffix starting at index i.
#
# Return the number of operations needed to make the string sorted. Since the
# answer can be too large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: s = "cba"
# Output: 5
# Explanation: The simulation goes as follows:
# Operation 1: i=2, j=2. Swap s[1] and s[2] to get s="cab", then reverse the
# suffix starting at 2. Now, s="cab".
# Operation 2: i=1, j=2. Swap s[0] and s[2] to get s="bac", then reverse the
# suffix starting at 1. Now, s="bca".
# Operation 3: i=2, j=2. Swap s[1] and s[2] to get s="bac", then reverse the
# suffix starting at 2. Now, s="bac".
# Operation 4: i=1, j=1. Swap s[0] and s[1] to get s="abc", then reverse the
# suffix starting at 1. Now, s="acb".
# Operation 5: i=2, j=2. Swap s[1] and s[2] to get s="abc", then reverse the
# suffix starting at 2. Now, s="abc".
#
# Example 2:
#
# Input: s = "aabaa"
# Output: 2
# Explanation: The simulation goes as follows:
# Operation 1: i=3, j=4. Swap s[2] and s[4] to get s="aaaab", then reverse the
# substring starting at 3. Now, s="aaaba".
# Operation 2: i=4, j=4. Swap s[3] and s[4] to get s="aaaab", then reverse the
# substring starting at 4. Now, s="aaaab".
#
# Constraints:
#
# 1 <= s.length <= 3000
#
# s consists only of lowercase English letters.
#

# @lc code=start
from collections import Counter


class Solution:
    def makeStringSorted(self, s: str) -> int:
        """
        Interview explanation:
        Count operations (next-permutation style moves) to sort string ascending
        = number of permutations strictly less than s among rearrangements of s
        (0-indexed rank of s among its anagrams).

        Algorithm (combinatorial rank):
        - Precompute factorials/inv factorials mod 10^9+7.
        - From left: for each pos, for each smaller remaining char c, add
          (count[c] * (n-1-i)!) / product(freq!).

        Complexity: O(n * 26) time, O(n) space.
        """
        MOD = 10**9 + 7
        n = len(s)
        fact = [1] * (n + 1)
        for i in range(1, n + 1):
            fact[i] = fact[i - 1] * i % MOD
        inv_fact = [1] * (n + 1)
        inv_fact[n] = pow(fact[n], MOD - 2, MOD)
        for i in range(n, 0, -1):
            inv_fact[i - 1] = inv_fact[i] * i % MOD

        cnt = [0] * 26
        for ch in s:
            cnt[ord(ch) - 97] += 1

        ans = 0
        for i, ch in enumerate(s):
            x = ord(ch) - 97
            for c in range(x):
                if cnt[c] == 0:
                    continue
                cnt[c] -= 1
                ways = fact[n - 1 - i]
                for v in cnt:
                    ways = ways * inv_fact[v] % MOD
                ans = (ans + ways) % MOD
                cnt[c] += 1
            cnt[x] -= 1
        return ans
# @lc code=end
