#
# @lc app=leetcode id=1316 lang=python3
#
# [1316] Distinct Echo Substrings
#
# https://leetcode.com/problems/distinct-echo-substrings/description/
#
# algorithms
# Hard (53.44%)
# Likes:    344
# Dislikes: 208
# Total Accepted:    23.6K
# Total Submissions: 44.1K
# Testcase Example:  "\"abcabcabc\""
#
# Return the number of distinct non-empty substrings of text that can be
# written as the concatenation of some string with itself (i.e. it can be
# written as a + a where a is some string).
#
# Example 1:
#
# Input: text = "abcabcabc"
# Output: 3
# Explanation: The 3 substrings are "abcabc", "bcabca" and "cabcab".
#
# Example 2:
#
# Input: text = "leetcodeleetcode"
# Output: 2
# Explanation: The 2 substrings are "ee" and "leetcodeleetcode".
#
# Constraints:
#
# 1 <= text.length <= 2000
#
# text has only lowercase English letters.
#

# @lc code=start
class Solution:
    def distinctEchoSubstrings(self, text: str) -> int:
        """
        Interview explanation:
        Echo substring = s+s (string concatenated with itself). Count distinct
        such substrings. Rolling hash compares halves in O(1) after O(n) prep.

        Algorithm (rolling hash):
        - For each even length 2*L and start i, if hash(text[i:i+L]) equals
          hash(text[i+L:i+2L]) add substring to set.

        Complexity: O(n^2) time, O(n^2) space for the set worst-case.
        """
        n = len(text)
        BASE, MOD = 911382323, 1_000_000_007
        powb = [1] * (n + 1)
        pref = [0] * (n + 1)
        for i, ch in enumerate(text):
            pref[i + 1] = (pref[i] * BASE + ord(ch)) % MOD
            powb[i + 1] = (powb[i] * BASE) % MOD

        def get(l, r):
            # hash of text[l:r]
            return (pref[r] - pref[l] * powb[r - l] % MOD) % MOD

        seen = set()
        for length in range(1, n // 2 + 1):
            for i in range(0, n - 2 * length + 1):
                if get(i, i + length) == get(i + length, i + 2 * length):
                    seen.add(text[i : i + 2 * length])
        return len(seen)

    def distinctEchoSubstrings_naive(self, text: str) -> int:
        """
        Interview explanation:
        Alternate: direct string compare of halves for each even window.

        Algorithm:
        - Same enumeration; compare slices equality; use a set.

        Complexity: O(n^3) naive slice compare / O(n^2) with care; O(n^2) space.
        """
        n = len(text)
        seen = set()
        for i in range(n):
            for j in range(i + 2, n + 1, 2):
                mid = (i + j) // 2
                if text[i:mid] == text[mid:j]:
                    seen.add(text[i:j])
        return len(seen)
# @lc code=end

