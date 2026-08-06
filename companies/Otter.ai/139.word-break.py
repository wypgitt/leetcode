"""
Approach: Dynamic programming over prefixes.
Data structure: a set stores dictionary words for O(1) lookup, and the dp array stores which prefixes can be segmented.
Interview logic: dp[i] is true if there is a dictionary word ending at i whose preceding prefix is also segmentable. Reuse of words is naturally allowed.
Complexity: O(n * L * W) in Python substring cost terms, where L is distinct word lengths and W is max word length; O(n + d) space.
Tests and edge cases: dp[0] is true for the empty prefix; unreachable prefixes stay false; overlapping dictionary words are handled by trying all lengths.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def wordBreak(self, s: str, wordDict: List[str]) -> bool:
        words = set(wordDict)
        lengths = {len(word) for word in words}
        dp = [False] * (len(s) + 1)
        dp[0] = True
        for i in range(1, len(s) + 1):
            dp[i] = any(i >= length and dp[i - length] and s[i - length:i] in words for length in lengths)
        return dp[-1]
# @lc code=end
