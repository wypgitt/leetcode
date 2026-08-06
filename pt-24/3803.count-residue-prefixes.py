#
# @lc app=leetcode id=3803 lang=python3
#
# [3803] Count Residue Prefixes
#
# https://leetcode.com/problems/count-residue-prefixes/description/
#
# algorithms
# Easy (65.89%)
# Likes:    66
# Dislikes: 1
# Total Accepted:    48.4K
# Total Submissions: 73.4K
# Testcase Example:  "\"abc\""
#
#
# You are given a string s consisting only of lowercase English letters.
#
# A prefix of s is called a residue if the number of distinct characters
# in the prefix is equal to len(prefix) % 3.
#
# Return the count of residue prefixes in s.
#
# A prefix of a string is a non-empty substring that starts from the
# beginning of the string and extends to any point within it.
#
# Example 1:
#
# Input: s = "abc"
#
# Output: 2
#
# Explanation:​​​​​​​
#
# Prefix "a" has 1 distinct character and length modulo 3 is 1, so it is a
# residue.
#
# Prefix "ab" has 2 distinct characters and length modulo 3 is 2, so it is
# a residue.
#
# Prefix "abc" does not satisfy the condition. Thus, the answer is 2.
#
# Example 2:
#
# Input: s = "dd"
#
# Output: 1
#
# Explanation:
#
# Prefix "d" has 1 distinct character and length modulo 3 is 1, so it is a
# residue.
#
# Prefix "dd" has 1 distinct character but length modulo 3 is 2, so it is
# not a residue. Thus, the answer is 1.
#
# Example 3:
#
# Input: s = "bob"
#
# Output: 2
#
# Explanation:
#
# Prefix "b" has 1 distinct character and length modulo 3 is 1, so it is a
# residue.
#
# Prefix "bo" has 2 distinct characters and length mod 3 is 2, so it is a
# residue. Thus, the answer is 2.
#
# Constraints:
#
# 1 <= s.length <= 100
#
# s contains only lowercase English letters.
#

# @lc code=start

class Solution:
    def residuePrefixes(self, s: str) -> int:
        """
        Interview explanation:
        Count prefixes whose distinct-char count equals length mod 3.

        Algorithm:
        - Scan left to right, track seen characters in a set.
        - For each prefix length i+1, check len(seen) == (i+1) % 3.

        Complexity: O(n) time, O(1) space (at most 26 letters).
        """
        seen = set()
        ans = 0
        for i, ch in enumerate(s):
            seen.add(ch)
            if len(seen) == (i + 1) % 3:
                ans += 1
        return ans

    def residuePrefixes_mask(self, s: str) -> int:
        """
        Interview explanation:
        Alternate: track distinct letters with a bit mask instead of a set.

        Algorithm:
        - OR in 1<<(ord(c)-'a'); popcount equals length mod 3.

        Complexity: O(n) time, O(1) space.
        """
        mask = 0
        ans = 0
        for i, ch in enumerate(s):
            mask |= 1 << (ord(ch) - ord("a"))
            if mask.bit_count() == (i + 1) % 3:
                ans += 1
        return ans
# @lc code=end
