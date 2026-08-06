#
# @lc app=leetcode id=1960 lang=python3
#
# [1960] Maximum Product of the Length of Two Palindromic Substrings
#
# https://leetcode.com/problems/maximum-product-of-the-length-of-two-palindromic-substrings/description/
#
# algorithms
# Hard (31.51%)
# Likes:    259
# Dislikes: 43
# Total Accepted:    5.4K
# Total Submissions: 17.3K
# Testcase Example:  "\"ababbb\""
#
# You are given a 0-indexed string s and are tasked with finding two
# non-intersecting palindromic substrings of odd length such that the product
# of their lengths is maximized.
#
# More formally, you want to choose four integers i, j, k, l such that 0 <= i
# <= j < k <= l < s.length and both the substrings s[i...j] and s[k...l] are
# palindromes and have odd lengths. s[i...j] denotes a substring from index i
# to index j inclusive.
#
# Return the maximum possible product of the lengths of the two
# non-intersecting palindromic substrings.
#
# A palindrome is a string that is the same forward and backward. A substring
# is a contiguous sequence of characters in a string.
#
# Example 1:
#
# Input: s = "ababbb"
# Output: 9
# Explanation: Substrings "aba" and "bbb" are palindromes with odd length.
# product = 3 * 3 = 9.
#
# Example 2:
#
# Input: s = "zaaaxbbby"
# Output: 9
# Explanation: Substrings "aaa" and "bbb" are palindromes with odd length.
# product = 3 * 3 = 9.
#
# Constraints:
#
# 2 <= s.length <= 10^5
#
# s consists of lowercase English letters.
#

# @lc code=start
class Solution:
    def maxProduct(self, s: str) -> int:
        """
        Interview explanation:
        Max product of lengths of two non-overlapping odd-length palindromic
        substrings. Manacher for odd radii; prefix/suffix max odd palindrome
        lengths; maximize pre[i]*suf[i+1].

        Algorithm:
        - Manacher odd: rad[i] radius (half-length floored).
        - For center i length = 2*rad[i]+1; update best ending/starting ranges
          into pref/suf max arrays.
        - ans = max pref[i]*suf[i+1].

        Complexity: O(n) time, O(n) space.
        """
        n = len(s)
        # Manacher for odd palindromes: d1[i] = radius (length = 2*d1[i]-1)
        d1 = [0] * n
        l = r = -1
        for i in range(n):
            k = 1 if i > r else min(d1[l + r - i], r - i + 1)
            while 0 <= i - k and i + k < n and s[i - k] == s[i + k]:
                k += 1
            d1[i] = k
            if i + k - 1 > r:
                l, r = i - k + 1, i + k - 1

        pref = [0] * n
        best = 0
        # For each center, palindrome covers [i-d1[i]+1, i+d1[i]-1]
        # longest odd palindrome ending at or before j
        j = 0
        for i in range(n):
            while j + d1[j] - 1 < i:
                j += 1
            best = max(best, 2 * (i - j) + 1)
            pref[i] = best

        suf = [0] * n
        best = 0
        j = n - 1
        for i in range(n - 1, -1, -1):
            while j - d1[j] + 1 > i:
                j -= 1
            best = max(best, 2 * (j - i) + 1)
            suf[i] = best

        ans = 0
        for i in range(n - 1):
            ans = max(ans, pref[i] * suf[i + 1])
        return ans

    def maxProduct_expand(self, s: str) -> int:
        """
        Interview explanation:
        Alternate (slower) clarity: expand odd palindromes from every center,
        maintain max length fully to the left/right of each cut.

        Algorithm:
        - For each center expand; update left_max[end] and right_max[start].
        - Prefix/suffix maxima; maximize product across a cut.

        Complexity: O(n^2) time, O(n) space.
        """
        n = len(s)
        left_max = [1] * n
        right_max = [1] * n
        for c in range(n):
            lo = hi = c
            while lo >= 0 and hi < n and s[lo] == s[hi]:
                length = hi - lo + 1
                left_max[hi] = max(left_max[hi], length)
                right_max[lo] = max(right_max[lo], length)
                lo -= 1
                hi += 1
        pref = [0] * n
        cur = 0
        for i in range(n):
            cur = max(cur, left_max[i])
            pref[i] = cur
        suf = [0] * n
        cur = 0
        for i in range(n - 1, -1, -1):
            cur = max(cur, right_max[i])
            suf[i] = cur
        return max(pref[i] * suf[i + 1] for i in range(n - 1))
# @lc code=end

