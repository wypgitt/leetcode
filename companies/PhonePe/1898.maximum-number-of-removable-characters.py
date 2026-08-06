#
# @lc app=leetcode id=1898 lang=python3
#
# [1898] Maximum Number of Removable Characters
#
# https://leetcode.com/problems/maximum-number-of-removable-characters/description/
#
# algorithms
# Medium (47.6%)
# Likes:    1061
# Dislikes: 137
# Total Accepted:    45.0K
# Total Submissions: 94.6K
# Testcase Example:  "\"abcacb\""
#
# You are given two strings s and p where p is a subsequence of s. You are also
# given a distinct 0-indexed integer array removable containing a subset of
# indices of s (s is also 0-indexed).
#
# You want to choose an integer k (0 <= k <= removable.length) such that, after
# removing k characters from s using the first k indices in removable, p is
# still a subsequence of s. More formally, you will mark the character at
# s[removable[i]] for each 0 <= i < k, then remove all marked characters and
# check if p is still a subsequence.
#
# Return the maximum k you can choose such that p is still a subsequence of s
# after the removals.
#
# A subsequence of a string is a new string generated from the original string
# with some characters (can be none) deleted without changing the relative
# order of the remaining characters.
#
# Example 1:
#
# Input: s = "abcacb", p = "ab", removable = [3,1,0]
# Output: 2
# Explanation: After removing the characters at indices 3 and 1, "abcacb"
# becomes "accb".
# "ab" is a subsequence of "accb".
# If we remove the characters at indices 3, 1, and 0, "abcacb" becomes "ccb",
# and "ab" is no longer a subsequence.
# Hence, the maximum k is 2.
#
# Example 2:
#
# Input: s = "abcbddddd", p = "abcd", removable = [3,2,1,4,5,6]
# Output: 1
# Explanation: After removing the character at index 3, "abcbddddd" becomes
# "abcddddd".
# "abcd" is a subsequence of "abcddddd".
#
# Example 3:
#
# Input: s = "abcab", p = "abc", removable = [0,1,2,3,4]
# Output: 0
# Explanation: If you remove the first index in the array removable, "abc" is
# no longer a subsequence.
#
# Constraints:
#
# 1 <= p.length <= s.length <= 10^5
#
# 0 <= removable.length < s.length
#
# 0 <= removable[i] < s.length
#
# p is a subsequence of s.
#
# s and p both consist of lowercase English letters.
#
# The elements in removable are distinct.
#

# @lc code=start
from typing import List


class Solution:
    def maximumRemovals(self, s: str, p: str, removable: List[int]) -> int:
        """
        Interview explanation:
        Remove first k indices listed in removable; maximize k so p stays a
        subsequence of s.

        Algorithm (binary search + subsequence check):
        - Binary search k; mark removable[:k] deleted; scan s matching p.

        Complexity: O((n+m) log R) time, O(R) space for the deleted set.
        """
        def ok(k: int) -> bool:
            deleted = set(removable[:k])
            j = 0
            for i, ch in enumerate(s):
                if i in deleted:
                    continue
                if j < len(p) and ch == p[j]:
                    j += 1
            return j == len(p)

        lo, hi = 0, len(removable)
        ans = 0
        while lo <= hi:
            mid = (lo + hi) // 2
            if ok(mid):
                ans = mid
                lo = mid + 1
            else:
                hi = mid - 1
        return ans

    def maximumRemovals_linear(self, s: str, p: str, removable: List[int]) -> int:
        """
        Interview explanation:
        Alternate: try k from len(removable) down to 0 with the same subsequence
        check (monotone, but linear probes).

        Algorithm:
        - For k = R..0: if p subsequence after deletions return k.

        Complexity: O(R*(n+m)) time.
        """
        def ok(k: int) -> bool:
            deleted = set(removable[:k])
            j = 0
            for i, ch in enumerate(s):
                if i in deleted:
                    continue
                if j < len(p) and ch == p[j]:
                    j += 1
            return j == len(p)

        for k in range(len(removable), -1, -1):
            if ok(k):
                return k
        return 0
# @lc code=end
