#
# @lc app=leetcode id=821 lang=python3
#
# [821] Shortest Distance to a Character
#
# https://leetcode.com/problems/shortest-distance-to-a-character/description/
#
# algorithms
# Easy (72.93%)
# Likes:    3350
# Dislikes: 197
# Total Accepted:    251K
# Total Submissions: 345K
# Testcase Example:  "\"loveleetcode\""
#
# Given a string s and a character c that occurs in s, return an array of
# integers answer where answer.length == s.length and answer[i] is the distance
# from index i to the closest occurrence of character c in s.
#
# The distance between two indices i and j is abs(i - j), where abs is the
# absolute value function.
#
# Example 1:
#
# Input: s = "loveleetcode", c = "e"
# Output: [3,2,1,0,1,0,0,1,2,2,1,0]
# Explanation: The character 'e' appears at indices 3, 5, 6, and 11
# (0-indexed).
# The closest occurrence of 'e' for index 0 is at index 3, so the distance is
# abs(0 - 3) = 3.
# The closest occurrence of 'e' for index 1 is at index 3, so the distance is
# abs(1 - 3) = 2.
# For index 4, there is a tie between the 'e' at index 3 and the 'e' at index
# 5, but the distance is still the same: abs(4 - 3) == abs(4 - 5) = 1.
# The closest occurrence of 'e' for index 8 is at index 6, so the distance is
# abs(8 - 6) = 2.
#
# Example 2:
#
# Input: s = "aaab", c = "b"
# Output: [3,2,1,0]
#
# Constraints:
#
# 1 <= s.length <= 10^4
#
# s[i] and c are lowercase English letters.
#
# It is guaranteed that c occurs at least once in s.
#

# @lc code=start

from typing import List


class Solution:
    def shortestToChar(self, s: str, c: str) -> List[int]:
        """
        Interview explanation:
        Two-pass: left-to-right track last seen c (distance growing), then
        right-to-left take min with distance from next c. Classic two-pass.

        Algorithm:
        - ans[i]=inf; pass L→R update from prev c; pass R→L min with next c.

        Complexity: O(n) time, O(n) space for answer.
        """
        n = len(s)
        ans = [n] * n
        prev = -n
        for i, ch in enumerate(s):
            if ch == c:
                prev = i
            ans[i] = i - prev
        prev = 2 * n
        for i in range(n - 1, -1, -1):
            if s[i] == c:
                prev = i
            ans[i] = min(ans[i], prev - i)
        return ans

    def shortestToChar_positions(self, s: str, c: str) -> List[int]:
        """
        Interview explanation:
        Alternate: collect all indices of c, then for each i binary-search /
        two-pointer nearest occurrence. Two-pointer on sorted positions is
        equally classic.

        Algorithm:
        - pos = indices of c; for each i advance pointer while next pos closer.

        Complexity: O(n) time, O(n) space.
        """
        pos = [i for i, ch in enumerate(s) if ch == c]
        ans = []
        j = 0
        for i in range(len(s)):
            while j + 1 < len(pos) and abs(pos[j + 1] - i) <= abs(pos[j] - i):
                j += 1
            ans.append(abs(pos[j] - i))
        return ans
# @lc code=end
