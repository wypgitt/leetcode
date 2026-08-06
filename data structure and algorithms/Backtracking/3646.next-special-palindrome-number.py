#
# @lc app=leetcode id=3646 lang=python3
#
# [3646] Next Special Palindrome Number
#
# https://leetcode.com/problems/next-special-palindrome-number/description/
#
# algorithms
# Hard (27.91%)
# Likes:    69
# Dislikes: 5
# Total Accepted:    12.2K
# Total Submissions: 43.7K
# Testcase Example:  "2"
#
#
# You are given an integer n.
#
# A number is called special if:
#
# It is a palindrome.
#
# Every digit k in the number appears exactly k times.
#
# Return the smallest special number strictly greater than n.
#
# Example 1:
#
# Input: n = 2
#
# Output: 22
#
# Explanation:
#
# 22 is the smallest special number greater than 2, as it is a palindrome
# and the digit 2 appears exactly 2 times.
#
# Example 2:
#
# Input: n = 33
#
# Output: 212
#
# Explanation:
#
# 212 is the smallest special number greater than 33, as it is a
# palindrome and the digits 1 and 2 appear exactly 1 and 2 times
# respectively.
#
# Constraints:
#
# 0 <= n <= 10^15
#

# @lc code=start
from itertools import combinations
from collections import Counter
from typing import List, Optional


class Solution:
    def specialPalindrome(self, n: int) -> int:
        """
        Interview explanation:
        Special numbers use each digit d exactly d times and form a
        palindrome — at most one odd digit. Search the next over all valid
        digit multisets.

        Algorithm:
        - Enumerate subsets of even digits {2,4,6,8} plus optional one odd.
        - For each multiset, build the smallest palindrome of that length
          greater than n (same length: next half arrangement; longer: sorted half).
        - Return the minimum candidate.

        Complexity: O(M * D) over multisets M and half length D (D ≤ 14).
        """
        odds = [1, 3, 5, 7, 9]
        evens = [2, 4, 6, 8]
        best = None
        for odd in [None] + odds:
            for r in range(len(evens) + 1):
                for ev in combinations(evens, r):
                    digits = list(ev)
                    if odd is not None:
                        digits.append(odd)
                    if not digits:
                        continue
                    val = self._next_for_multiset(n, digits)
                    if val is not None and (best is None or val < best):
                        best = val
        return best

    def _next_for_multiset(self, n: int, digits: List[int]) -> Optional[int]:
        """Smallest special palindrome > n using exactly these digits."""
        cnt = Counter({d: d for d in digits})
        length = sum(cnt.values())
        ns = str(n)
        if length < len(ns):
            return None
        half_cnt = Counter()
        mid = None
        for d, c in cnt.items():
            if c // 2:
                half_cnt[d] = c // 2
            if c % 2:
                mid = d
        half_len = length // 2
        if length > len(ns):
            half = []
            for d in sorted(half_cnt):
                half.extend([d] * half_cnt[d])
            s = "".join(map(str, half))
            m = "" if mid is None else str(mid)
            return int(s + m + s[::-1])
        target = [int(c) for c in ns]
        prefix = target[:half_len]
        if Counter(prefix) == half_cnt:
            m = "" if mid is None else str(mid)
            pal = "".join(map(str, prefix)) + m + "".join(map(str, prefix[::-1]))
            if int(pal) > n:
                return int(pal)
        arr = self._next_strict_arr(half_cnt, prefix)
        if arr is None:
            return None
        m = "" if mid is None else str(mid)
        return int("".join(map(str, arr)) + m + "".join(map(str, arr[::-1])))

    def _next_strict_arr(self, counts: Counter, target: List[int]) -> Optional[List[int]]:
        """Lexicographically smallest sequence with exact counts, > target."""
        n = len(target)
        ans = None
        cnt = Counter(counts)

        def dfs(i: int, path: list, equal: bool) -> None:
            nonlocal ans
            if ans is not None:
                return
            if i == n:
                if not equal:
                    ans = path[:]
                return
            for d in range(1, 10):
                if cnt[d] == 0:
                    continue
                if equal and d < target[i]:
                    continue
                cnt[d] -= 1
                path.append(d)
                dfs(i + 1, path, equal and d == target[i])
                path.pop()
                cnt[d] += 1
                if ans is not None:
                    return

        dfs(0, [], True)
        return ans
# @lc code=end

