"""
Approach: Reverse the whole character array, then reverse each word in place.
Data structure: two-pointer swaps mutate the list without allocating another list of characters.
Interview logic: reversing all characters puts words in reverse order but each word's letters are backward. Reversing each word fixes the letters while preserving word order.
Complexity: O(n) time, O(1) extra space.
Tests and edge cases: one word; multiple single-character words; spaces separate words and are preserved as single spaces by the problem constraints.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def reverseWords(self, s: List[str]) -> None:
        def rev(left: int, right: int) -> None:
            while left < right:
                s[left], s[right] = s[right], s[left]
                left += 1
                right -= 1
        rev(0, len(s) - 1)
        start = 0
        for i in range(len(s) + 1):
            if i == len(s) or s[i] == ' ':
                rev(start, i - 1)
                start = i + 1
# @lc code=end
