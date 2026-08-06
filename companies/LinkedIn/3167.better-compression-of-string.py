#
# @lc app=leetcode id=3167 lang=python3
#
# [3167] Better Compression of String
#
# https://leetcode.com/problems/better-compression-of-string/description/
#
# algorithms
# Medium (75.44%)
# Likes:    19
# Dislikes: 4
# Total Accepted:    6.1K
# Total Submissions: 8.1K
# Testcase Example:  "\"a3c9b2c1\""
#
#
# You are given a string compressed representing a compressed version of a
# string. The format is a character followed by its frequency. For
# example, "a3b1a1c2" is a compressed version of the string "aaabacc".
#
# We seek a better compression with the following conditions:
#
# Each character should appear only once in the compressed version.
#
# The characters should be in alphabetical order.
#
# Return the better compression of compressed.
#
# Note: In the better version of compression, the order of letters may
# change, which is acceptable.
#
# Example 1:
#
# Input: compressed = "a3c9b2c1"
#
# Output: "a3b2c10"
#
# Explanation:
#
# Characters "a" and "b" appear only once in the input, but "c" appears
# twice, once with a size of 9 and once with a size of 1.
#
# Hence, in the resulting string, it should have a size of 10.
#
# Example 2:
#
# Input: compressed = "c2b3a1"
#
# Output: "a1b3c2"
#
# Example 3:
#
# Input: compressed = "a2b4c1"
#
# Output: "a2b4c1"
#
# Constraints:
#
# 1 <= compressed.length <= 6 * 10^4
#
# compressed consists only of lowercase English letters and digits.
#
# compressed is a valid compression, i.e., each character is followed by
# its frequency.
#
# Frequencies are in the range [1, 10^4] and have no leading zeroes.
#

# @lc code=start
from collections import defaultdict


class Solution:
    def betterCompression(self, compressed: str) -> str:
        """
        Interview explanation:
        Parse char+frequency tokens, merge frequencies per character, then
        emit characters in alphabetical order with total counts.

        Algorithm:
        - Scan: letter then following digits form a number; add into a map.
        - Rebuild sorted by character key.

        Complexity: O(n + A log A) time (A <= 26), O(A) space.
        """
        freq: dict[str, int] = defaultdict(int)
        i, n = 0, len(compressed)
        while i < n:
            c = compressed[i]
            i += 1
            j = i
            while j < n and compressed[j].isdigit():
                j += 1
            freq[c] += int(compressed[i:j])
            i = j
        return "".join(f"{c}{freq[c]}" for c in sorted(freq))

    def betterCompression_regex(self, compressed: str) -> str:
        """
        Interview explanation:
        Alternate: regex-split tokens of form ([a-z])(\\d+), then same merge.

        Algorithm:
        - findall letter+digits; aggregate; join sorted.

        Complexity: O(n) time, O(A) space.
        """
        import re
        from collections import Counter

        freq: Counter = Counter()
        for c, num in re.findall(r"([a-z])(\d+)", compressed):
            freq[c] += int(num)
        return "".join(f"{c}{freq[c]}" for c in sorted(freq))
# @lc code=end
