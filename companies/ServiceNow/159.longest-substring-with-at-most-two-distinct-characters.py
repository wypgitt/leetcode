"""
Approach: Sliding window with character counts.
Data structure: a hash map counts characters currently inside the window so we know when there are more than two distinct characters.
Interview logic: expand the right boundary one character at a time. If the window becomes invalid, move left until only two distinct characters remain, then record the maximum length.
Complexity: O(n) time because each pointer moves forward at most n times; O(1) space because at most three character counts are kept during shrinking.
Tests and edge cases: empty string returns 0; strings with <=2 distinct characters return full length; alternating third characters force shrinking.
"""
from __future__ import annotations
from collections import defaultdict

# @lc code=start
from collections import defaultdict
class Solution:
    def lengthOfLongestSubstringTwoDistinct(self, s: str) -> int:
        counts = defaultdict(int)
        left = best = 0
        for right, ch in enumerate(s):
            counts[ch] += 1
            while len(counts) > 2:
                old = s[left]
                counts[old] -= 1
                if counts[old] == 0:
                    del counts[old]
                left += 1
            best = max(best, right - left + 1)
        return best
# @lc code=end
