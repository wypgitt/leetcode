#
# @lc app=leetcode id=3816 lang=python3
#
# [3816] Lexicographically Smallest String After Deleting Duplicate Characters
#
# https://leetcode.com/problems/lexicographically-smallest-string-after-deleting-duplicate-characters/description/
#
# algorithms
# Hard (21.10%)
# Likes:    45
# Dislikes: 4
# Total Accepted:    6.1K
# Total Submissions: 29.1K
# Testcase Example:  "\"aaccb\""
#
#
# You are given a string s that consists of lowercase English letters.
#
# You can perform the following operation any number of times (possibly
# zero times):
#
# Choose any letter that appears at least twice in the current string s
# and delete any one occurrence.
#
# Return the lexicographically smallest resulting string that can be
# formed this way.
#
# Example 1:
#
# Input: s = "aaccb"
#
# Output: "aacb"
#
# Explanation:
#
# We can form the strings "acb", "aacb", "accb", and "aaccb". "aacb" is
# the lexicographically smallest one.
#
# For example, we can obtain "aacb" by choosing 'c' and deleting its first
# occurrence.
#
# Example 2:
#
# Input: s = "z"
#
# Output: "z"
#
# Explanation:
#
# We cannot perform any operations. The only string we can form is "z".
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s contains lowercase English letters only.
#

# @lc code=start
class Solution:
    def lexSmallestAfterDeletion(self, s: str) -> str:
        """
        Interview explanation:
        Delete duplicate letters until each remaining letter is unique once, and
        the resulting subsequence is lexicographically smallest.

        Algorithm:
        - Keep last occurrence of each distinct letter as a "must cover" deadline.
        - Greedily append the smallest letter that still has an occurrence after
          the previous pick and leaves all other missing letters finishable.
        - Repeat until every distinct letter has been chosen once.

        Complexity: O(26 * n) time, O(n) space.
        """
        positions = [[] for _ in range(26)]
        for index, ch in enumerate(s):
            positions[ord(ch) - ord("a")].append(index)

        last = [-1] * 26
        missing = 0
        for ch in range(26):
            if positions[ch]:
                last[ch] = positions[ch][-1]
                missing |= 1 << ch

        ptr = [0] * 26
        start = 0
        answer = []

        while missing:
            for ch in range(26):
                pos_list = positions[ch]
                while ptr[ch] < len(pos_list) and pos_list[ptr[ch]] < start:
                    ptr[ch] += 1

                if ptr[ch] == len(pos_list):
                    continue

                index = pos_list[ptr[ch]]
                new_missing = missing & ~(1 << ch)
                if self._can_finish_after(index, new_missing, last):
                    answer.append(chr(ord("a") + ch))
                    start = index + 1
                    missing = new_missing
                    break

        return "".join(answer)

    def _can_finish_after(self, index: int, missing: int, last: list[int]) -> bool:
        for ch in range(26):
            if missing >> ch & 1 and last[ch] <= index:
                return False
        return True
# @lc code=end
