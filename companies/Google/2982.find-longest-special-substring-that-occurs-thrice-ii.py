#
# @lc app=leetcode id=2982 lang=python3
#
# [2982] Find Longest Special Substring That Occurs Thrice II
#
# https://leetcode.com/problems/find-longest-special-substring-that-occurs-thrice-ii/description/
#
# algorithms
# Medium (39.38%)
# Likes:    414
# Dislikes: 34
# Total Accepted:    32.9K
# Total Submissions: 83.6K
# Testcase Example:  "\"aaaa\""
#
#
# You are given a string s that consists of lowercase English letters.
#
# A string is called special if it is made up of only a single character.
# For example, the string "abc" is not special, whereas the strings "ddd",
# "zz", and "f" are special.
#
# Return the length of the longest special substring of s which occurs at
# least thrice, or -1 if no special substring occurs at least thrice.
#
# A substring is a contiguous non-empty sequence of characters within a
# string.
#
# Example 1:
#
# Input: s = "aaaa"
# Output: 2
# Explanation: The longest special substring which occurs thrice is "aa":
# substrings "aaaa", "aaaa", and "aaaa".
# It can be shown that the maximum length achievable is 2.
#
# Example 2:
#
# Input: s = "abcdef"
# Output: -1
# Explanation: There exists no special substring which occurs at least
# thrice. Hence return -1.
#
# Example 3:
#
# Input: s = "abcaba"
# Output: 1
# Explanation: The longest special substring which occurs thrice is "a":
# substrings "abcaba", "abcaba", and "abcaba".
# It can be shown that the maximum length achievable is 1.
#
# Constraints:
#
# 3 <= s.length <= 5 * 10^5
#
# s consists of only lowercase English letters.
#

# @lc code=start

from collections import defaultdict


class Solution:
    def maximumLength(self, s: str) -> int:
        """
        Interview explanation:
        Special substring = run of one letter. Find max length that occurs >= 3
        times (overlapping within a run counts). n up to 5e5.

        Algorithm:
        - Binary search length x; for each run of char c length L, add
          max(0, L-x+1) occurrences; check if any char totals >= 3.

        Complexity: O(n log n) time, O(1) extra space (26 letters).
        """
        n = len(s)

        def check(x: int) -> bool:
            cnt = defaultdict(int)
            i = 0
            while i < n:
                j = i + 1
                while j < n and s[j] == s[i]:
                    j += 1
                cnt[s[i]] += max(0, j - i - x + 1)
                i = j
            return max(cnt.values(), default=0) >= 3

        lo, hi = 0, n
        while lo < hi:
            mid = (lo + hi + 1) >> 1
            if check(mid):
                lo = mid
            else:
                hi = mid - 1
        return -1 if lo == 0 else lo

    def maximumLength_top3_runs(self, s: str) -> int:
        """
        Interview explanation:
        Alternate O(n): per character keep the three longest runs; derive the
        max length that can appear thrice from those runs alone.

        Algorithm:
        - Scan runs; for each char's top-3 lengths L0>=L1>=L2:
          L0-2 (one run), min(L0-1, L1) (two runs), L2 (three runs).

        Complexity: O(n) time, O(1) space.
        """
        from collections import defaultdict

        runs: dict[str, list[int]] = defaultdict(list)
        i, n = 0, len(s)
        while i < n:
            j = i + 1
            while j < n and s[j] == s[i]:
                j += 1
            runs[s[i]].append(j - i)
            i = j

        ans = -1
        for lens in runs.values():
            lens.sort(reverse=True)
            top = (lens + [0, 0, 0])[:3]
            l0, l1, l2 = top
            if l0 >= 3:
                ans = max(ans, l0 - 2)
            if l1:
                ans = max(ans, min(l0 - 1, l1))
            if l2:
                ans = max(ans, l2)
        return ans
# @lc code=end
