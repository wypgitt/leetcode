#
# @lc app=leetcode id=1461 lang=python3
#
# [1461] Check If a String Contains All Binary Codes of Size K
#
# https://leetcode.com/problems/check-if-a-string-contains-all-binary-codes-of-size-k/description/
#
# algorithms
# Medium (61.63%)
# Likes:    2736
# Dislikes: 116
# Total Accepted:    270K
# Total Submissions: 438K
# Testcase Example:  "\"00110110\""
#
# Given a binary string s and an integer k, return true if every binary code of
# length k is a substring of s. Otherwise, return false.
#
# Example 1:
#
# Input: s = "00110110", k = 2
# Output: true
# Explanation: The binary codes of length 2 are "00", "01", "10" and "11". They
# can be all found as substrings at indices 0, 1, 3 and 2 respectively.
#
# Example 2:
#
# Input: s = "0110", k = 1
# Output: true
# Explanation: The binary codes of length 1 are "0" and "1", it is clear that
# both exist as a substring.
#
# Example 3:
#
# Input: s = "0110", k = 2
# Output: false
# Explanation: The binary code "00" is of length 2 and does not exist in the
# array.
#
# Constraints:
#
# 1 <= s.length <= 5 * 10^5
#
# s[i] is either '0' or '1'.
#
# 1 <= k <= 20
#

# @lc code=start
class Solution:
    def hasAllCodes(self, s: str, k: int) -> bool:
        """
        Interview explanation:
        Check whether every binary string of length k appears as a substring.
        Need 2^k distinct substrings of length k.

        Algorithm:
        - Add all s[i:i+k] to a set; return len(set) == 1<<k.

        Complexity: O(n*k) time (or O(n) with rolling), O(min(n,2^k)*k) space.
        """
        need = 1 << k
        if len(s) < k + need - 1:
            return False
        seen = set()
        for i in range(len(s) - k + 1):
            seen.add(s[i : i + k])
            if len(seen) == need:
                return True
        return False

    def hasAllCodes_rolling(self, s: str, k: int) -> bool:
        """
        Interview explanation:
        Alternate: rolling integer hash of k-bit window; bitset/bool array of
        size 2^k.

        Algorithm:
        - Parse first k bits; slide: x = ((x<<1) & mask) | bit; mark seen.

        Complexity: O(n) time, O(2^k) space.
        """
        need = 1 << k
        if len(s) < k:
            return False
        seen = [False] * need
        mask = need - 1
        x = int(s[:k], 2)
        seen[x] = True
        got = 1
        for i in range(k, len(s)):
            x = ((x << 1) & mask) | (ord(s[i]) - 48)
            if not seen[x]:
                seen[x] = True
                got += 1
                if got == need:
                    return True
        return got == need
# @lc code=end
