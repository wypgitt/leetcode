#
# @lc app=leetcode id=2213 lang=python3
#
# [2213] Longest Substring of One Repeating Character
#
# https://leetcode.com/problems/longest-substring-of-one-repeating-character/description/
#
# algorithms
# Hard (34.91%)
# Likes:    331
# Dislikes: 84
# Total Accepted:    7.2K
# Total Submissions: 20.6K
# Testcase Example:  "\"babacc\"\n\"bcb\"\n[1,3,3]"
#
# You are given a 0-indexed string s. You are also given a 0-indexed string
# queryCharacters of length k and a 0-indexed array of integer indices
# queryIndices of length k, both of which are used to describe k queries.
#
# The i^th query updates the character in s at index queryIndices[i] to the
# character queryCharacters[i].
#
# Return an array lengths of length k where lengths[i] is the length of the
# longest substring of s consisting of only one repeating character after the
# i^th query is performed.
#
#
#
# Example 1:
#
# Input: s = "babacc", queryCharacters = "bcb", queryIndices = [1,3,3]
# Output: [3,3,4]
# Explanation:
# - 1^st query updates s = "bbbacc". The longest substring consisting of one
# repeating character is "bbb" with length 3.
# - 2^nd query updates s = "bbbccc".
#   The longest substring consisting of one repeating character can be "bbb" or
# "ccc" with length 3.
# - 3^rd query updates s = "bbbbcc". The longest substring consisting of one
# repeating character is "bbbb" with length 4.
# Thus, we return [3,3,4].
#
# Example 2:
#
# Input: s = "abyzz", queryCharacters = "aa", queryIndices = [2,1]
# Output: [2,3]
# Explanation:
# - 1^st query updates s = "abazz". The longest substring consisting of one
# repeating character is "zz" with length 2.
# - 2^nd query updates s = "aaazz". The longest substring consisting of one
# repeating character is "aaa" with length 3.
# Thus, we return [2,3].
#
#
#
# Constraints:
#
#
# 1 <= s.length <= 10^5
#
#
# s consists of lowercase English letters.
#
#
# k == queryCharacters.length == queryIndices.length
#
#
# 1 <= k <= 10^5
#
#
# queryCharacters consists of lowercase English letters.
#
#
# 0 <= queryIndices[i] < s.length
#

# @lc code=start
from typing import List


class SegmentTree:
    __slots__ = ("n", "s", "pref", "suf", "best", "left_ch", "right_ch", "size")

    def __init__(self, s: str):
        """
        Interview explanation:
        Build a segment tree over string s supporting point updates and querying
        the longest same-character run.

        Algorithm:
        - Leaf = single char run of 1; internal nodes merge pref/suf/best.

        Complexity: O(n) build time, O(n) space.
        """
        self.n = len(s)
        self.s = list(s)
        m = 4 * self.n
        self.pref = [0] * m
        self.suf = [0] * m
        self.best = [0] * m
        self.left_ch = [""] * m
        self.right_ch = [""] * m
        self.size = [0] * m
        self._build(1, 0, self.n - 1)

    def _pull(self, idx: int, l: int, r: int) -> None:
        left, right = idx * 2, idx * 2 + 1
        self.left_ch[idx] = self.left_ch[left]
        self.right_ch[idx] = self.right_ch[right]
        self.size[idx] = self.size[left] + self.size[right]
        self.best[idx] = max(self.best[left], self.best[right])
        self.pref[idx] = self.pref[left]
        self.suf[idx] = self.suf[right]
        if self.right_ch[left] == self.left_ch[right]:
            self.best[idx] = max(
                self.best[idx], self.suf[left] + self.pref[right]
            )
            if self.pref[left] == self.size[left]:
                self.pref[idx] = self.size[left] + self.pref[right]
            if self.suf[right] == self.size[right]:
                self.suf[idx] = self.size[right] + self.suf[left]

    def _build(self, idx: int, l: int, r: int) -> None:
        if l == r:
            self.pref[idx] = self.suf[idx] = self.best[idx] = self.size[idx] = 1
            self.left_ch[idx] = self.right_ch[idx] = self.s[l]
            return
        mid = (l + r) // 2
        self._build(idx * 2, l, mid)
        self._build(idx * 2 + 1, mid + 1, r)
        self._pull(idx, l, r)

    def update(self, pos: int, ch: str) -> None:
        """
        Interview explanation:
        Point-update character at index pos to ch and refresh aggregates.

        Algorithm:
        - Recurse to leaf; pull parents.

        Complexity: O(log n) time, O(1) extra space.
        """
        self._update(1, 0, self.n - 1, pos, ch)

    def _update(self, idx: int, l: int, r: int, pos: int, ch: str) -> None:
        if l == r:
            self.left_ch[idx] = self.right_ch[idx] = ch
            self.s[pos] = ch
            return
        mid = (l + r) // 2
        if pos <= mid:
            self._update(idx * 2, l, mid, pos, ch)
        else:
            self._update(idx * 2 + 1, mid + 1, r, pos, ch)
        self._pull(idx, l, r)

    def query_best(self) -> int:
        """
        Interview explanation:
        Return the longest single-character run in the current string.

        Algorithm:
        - Read root best field.

        Complexity: O(1) time, O(1) space.
        """
        return self.best[1]


class Solution:
    def longestRepeating(self, s: str, queryCharacters: str, queryIndices: List[int]) -> List[int]:
        """
        Interview explanation:
        After each update s[queryIndices[i]] = queryCharacters[i], report the
        longest run of a single character in s.

        Algorithm:
        (segment tree)
        - Node stores pref/suf/best run lengths and border chars; merge across
          mid when border chars match. Point update + read root best.

        Complexity: O((n+q) log n) time, O(n) space.
        """
        st = SegmentTree(s)
        ans = []
        for ch, i in zip(queryCharacters, queryIndices):
            st.update(i, ch)
            ans.append(st.query_best())
        return ans
# @lc code=end
