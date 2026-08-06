"""
Approach: Split into words, reverse the word list, and join with one space.
Data structure: a list of tokens separates meaningful words from irrelevant whitespace.
Interview logic: str.split() without an argument removes leading/trailing whitespace and collapses runs, exactly matching the output formatting requirement.
Complexity: O(n) time, O(n) space.
Tests and edge cases: multiple spaces collapse; leading and trailing spaces vanish; one word is unchanged.
"""
from __future__ import annotations

# @lc code=start
class Solution:
    def reverseWords(self, s: str) -> str:
        return ' '.join(reversed(s.split()))
# @lc code=end
