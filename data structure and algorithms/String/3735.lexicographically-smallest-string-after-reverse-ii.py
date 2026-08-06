#
# @lc app=leetcode id=3735 lang=python3
#
# [3735] Lexicographically Smallest String After Reverse II
#
# https://leetcode.com/problems/lexicographically-smallest-string-after-reverse-ii/description/
#
# algorithms
# Hard (48.41%)
# Likes:    2
# Dislikes: 1
# Total Accepted:    350
# Total Submissions: 723
# Testcase Example:  "\"dcab\""
#
#
# You are given a string s of length n consisting of lowercase English
# letters.
#
# You must perform exactly one operation by choosing any integer k such
# that 1 <= k <= n and either:
#
# reverse the first k characters of s, or
#
# reverse the last k characters of s.
#
# Return the lexicographically smallest string that can be obtained after
# exactly one such operation.
#
# Example 1:
#
# Input: s = "dcab"
#
# Output: "acdb"
#
# Explanation:
#
# Choose k = 3, reverse the first 3 characters.
#
# Reverse "dca" to "acd", resulting string s = "acdb", which is the
# lexicographically smallest string achievable.
#
# Example 2:
#
# Input: s = "abba"
#
# Output: "aabb"
#
# Explanation:
#
# Choose k = 3, reverse the last 3 characters.
#
# Reverse "bba" to "abb", so the resulting string is "aabb", which is the
# lexicographically smallest string achievable.
#
# Example 3:
#
# Input: s = "zxy"
#
# Output: "xzy"
#
# Explanation:
#
# Choose k = 2, reverse the first 2 characters.
#
# Reverse "zx" to "xz", so the resulting string is "xzy", which is the
# lexicographically smallest string achievable.
#
# Constraints:
#
# 1 <= n == s.length <= 10^5
#
# s consists of lowercase English letters.
#

# @lc code=start
class Solution:
    def lexSmallest(self, s: str) -> str:
        """
        Interview explanation:
        Same operation set as the medium version but n <= 1e5. Compare the 2n
        candidate strings via rolling hashes + binary search for the first
        differing index instead of materializing each string.

        Algorithm:
        - Best answer starts with min(s); only test prefix reverses with that start.
        - Suffix reverses that can beat the identity need s[-k] >= s[-1].
        - Keep the lexicographically smallest (k, type) under hash comparison.

        Complexity: O(n log n) time, O(n) space.
        """
        MOD, BASE = 10**9 + 7, 29
        n = len(s)
        pref = [0] * (n + 1)
        for i, ch in enumerate(s):
            pref[i + 1] = (pref[i] * BASE + ord(ch)) % MOD
        suff = [0] * (n + 1)
        for i in range(n - 1, -1, -1):
            suff[i] = (suff[i + 1] * BASE + ord(s[i])) % MOD
        pw = [1] * (n + 1)
        for i in range(n):
            pw[i + 1] = pw[i] * BASE % MOD

        def ph(l: int, r: int) -> int:
            return (pref[r + 1] - pref[l] * pw[r - l + 1]) % MOD if l <= r else 0

        def sh(l: int, r: int) -> int:
            return (suff[l] - suff[r + 1] * pw[r - l + 1]) % MOD if l <= r else 0

        def thash(k: int, typ: int, length: int) -> int:
            if typ == 0:
                if length <= k:
                    return sh(k - length, k - 1)
                return (sh(0, k - 1) * pw[length - k] + ph(k, length - 1)) % MOD
            nk = n - k
            if length <= nk:
                return ph(0, length - 1)
            return (ph(0, nk - 1) * pw[length - nk] + sh(n - (length - nk), n - 1)) % MOD

        def char_at(k: int, typ: int, idx: int) -> str:
            if typ == 0:
                return s[k - 1 - idx] if idx < k else s[idx]
            return s[idx] if idx < n - k else s[n - 1 - (idx - (n - k))]

        best_k, best_t = 1, 0

        def better(k: int, typ: int) -> bool:
            lo, hi = 0, n - 1
            while lo <= hi:
                mid = (lo + hi) // 2
                if thash(k, typ, mid + 1) != thash(best_k, best_t, mid + 1):
                    hi = mid - 1
                else:
                    lo = mid + 1
            return lo < n and char_at(k, typ, lo) < char_at(best_k, best_t, lo)

        mn = min(s)
        for k in range(1, n + 1):
            if s[k - 1] == mn and better(k, 0):
                best_k, best_t = k, 0
        for k in range(1, n + 1):
            if s[-k] >= s[-1] and better(k, 1):
                best_k, best_t = k, 1
        if best_t == 0:
            return s[:best_k][::-1] + s[best_k:]
        return s[: n - best_k] + s[n - best_k :][::-1]

    def lexSmallest_brute(self, s: str) -> str:
        """
        Interview explanation:
        Alternate: enumerate every k (fine for smaller n / verification).

        Algorithm:
        - Min over all prefix/suffix reverses.

        Complexity: O(n^2) time, O(n) space.
        """
        ans = s
        n = len(s)
        for k in range(1, n + 1):
            ans = min(ans, s[:k][::-1] + s[k:], s[: n - k] + s[n - k :][::-1])
        return ans
# @lc code=end

