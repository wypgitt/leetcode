#
# @lc app=leetcode id=3458 lang=python3
#
# [3458] Select K Disjoint Special Substrings
#
# https://leetcode.com/problems/select-k-disjoint-special-substrings/description/
#
# algorithms
# Medium (19.48%)
# Likes:    145
# Dislikes: 15
# Total Accepted:    11.7K
# Total Submissions: 60.2K
# Testcase Example:  "\"abcdbaefab\"\n2"
#
#
# Given a string s of length n and an integer k, determine whether it is
# possible to select k disjoint special substrings.
#
# A special substring is a substring where:
#
# Any character present inside the substring should not appear outside it
# in the string.
#
# The substring is not the entire string s.
#
# Note that all k substrings must be disjoint, meaning they cannot
# overlap.
#
# Return true if it is possible to select k such disjoint special
# substrings; otherwise, return false.
#
# Example 1:
#
# Input: s = "abcdbaefab", k = 2
#
# Output: true
#
# Explanation:
#
# We can select two disjoint special substrings: "cd" and "ef".
#
# "cd" contains the characters 'c' and 'd', which do not appear elsewhere
# in s.
#
# "ef" contains the characters 'e' and 'f', which do not appear elsewhere
# in s.
#
# Example 2:
#
# Input: s = "cdefdc", k = 3
#
# Output: false
#
# Explanation:
#
# There can be at most 2 disjoint special substrings: "e" and "f". Since k
# = 3, the output is false.
#
# Example 3:
#
# Input: s = "abeabe", k = 0
#
# Output: true
#
# Constraints:
#
# 2 <= n == s.length <= 5 * 10^4
#
# 0 <= k <= 26
#
# s consists only of lowercase English letters.
#

# @lc code=start

class Solution:
    def maxSubstringLength(self, s: str, k: int) -> bool:
        """
        Interview explanation:
        A special substring's characters never appear outside it, and it is not the
        whole string. Decide whether >= k disjoint specials exist.

        Algorithm:
        - For each char's first occurrence, expand [first,last] like partition-labels
          until closed; keep spans that are valid (no char's first is left of L) and
          not the full string.
        - Greedily pick non-overlapping intervals by earliest end; compare count to k.

        Complexity: O(n) time, O(n) space for intervals (≤26 useful spans).
        """
        if k == 0:
            return True
        n = len(s)
        first = [-1] * 26
        last = [-1] * 26
        for i, ch in enumerate(s):
            a = ord(ch) - 97
            if first[a] == -1:
                first[a] = i
            last[a] = i

        intervals: list[tuple[int, int]] = []
        for i in range(n):
            a = ord(s[i]) - 97
            if i != first[a]:
                continue
            j = last[a]
            pos = i
            while pos <= j:
                j = max(j, last[ord(s[pos]) - 97])
                pos += 1
            if any(first[ord(s[p]) - 97] < i for p in range(i, j + 1)):
                continue
            if i == 0 and j == n - 1:
                continue
            intervals.append((i, j))

        intervals.sort(key=lambda x: x[1])
        count = 0
        end = -1
        for L, R in intervals:
            if L > end:
                count += 1
                end = R
        return count >= k
# @lc code=end
