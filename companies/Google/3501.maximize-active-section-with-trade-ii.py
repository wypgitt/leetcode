#
# @lc app=leetcode id=3501 lang=python3
#
# [3501] Maximize Active Section with Trade II
#
# https://leetcode.com/problems/maximize-active-section-with-trade-ii/description/
#
# algorithms
# Hard (64.69%)
# Likes:    182
# Dislikes: 42
# Total Accepted:    58.6K
# Total Submissions: 90.5K
# Testcase Example:  "\"01\"\n[[0,1]]"
#
#
# You are given a binary string s of length n, where:
#
# '1' represents an active section.
#
# '0' represents an inactive section.
#
# You can perform at most one trade to maximize the number of active
# sections in s. In a trade, you:
#
# Convert a contiguous block of '1's that is surrounded by '0's to all
# '0's.
#
# Afterward, convert a contiguous block of '0's that is surrounded by '1's
# to all '1's.
#
# Additionally, you are given a 2D array queries, where queries[i] = [l_i,
# r_i] represents a substring s[l_i...r_i].
#
# For each query, determine the maximum possible number of active sections
# in s after making the optimal trade on the substring s[l_i...r_i].
#
# Return an array answer, where answer[i] is the result for queries[i].
#
# Note
#
# For each query, treat s[l_i...r_i] as if it is augmented with a '1' at
# both ends, forming t = '1' + s[l_i...r_i] + '1'. The augmented '1's do
# not contribute to the final count.
#
# The queries are independent of each other.
#
# Example 1:
#
# Input: s = "01", queries = [[0,1]]
#
# Output: [1]
#
# Explanation:
#
# Because there is no block of '1's surrounded by '0's, no valid trade is
# possible. The maximum number of active sections is 1.
#
# Example 2:
#
# Input: s = "0100", queries = [[0,3],[0,2],[1,3],[2,3]]
#
# Output: [4,3,1,1]
#
# Explanation:
#
# Query [0, 3] → Substring "0100" → Augmented to "101001"
#
#         Choose "0100", convert "0100" → "0000" → "1111".
#
#         The final string without augmentation is "1111". The maximum
# number of active sections is 4.
#
# Query [0, 2] → Substring "010" → Augmented to "10101"
#
#         Choose "010", convert "010" → "000" → "111".
#
#         The final string without augmentation is "1110". The maximum
# number of active sections is 3.
#
# Query [1, 3] → Substring "100" → Augmented to "11001"
#
#         Because there is no block of '1's surrounded by '0's, no valid
# trade is possible. The maximum number of active sections is 1.
#
# Query [2, 3] → Substring "00" → Augmented to "1001"
#
#         Because there is no block of '1's surrounded by '0's, no valid
# trade is possible. The maximum number of active sections is 1.
#
# Example 3:
#
# Input: s = "1000100", queries = [[1,5],[0,6],[0,4]]
#
# Output: [6,7,2]
#
# Explanation:
#
# Query [1, 5] → Substring "00010" → Augmented to "1000101"
#
#         Choose "00010", convert "00010" → "00000" → "11111".
#
#         The final string without augmentation is "1111110". The maximum
# number of active sections is 6.
#
# Query [0, 6] → Substring "1000100" → Augmented to "110001001"
#
#         Choose "000100", convert "000100" → "000000" → "111111".
#
#         The final string without augmentation is "1111111". The maximum
# number of active sections is 7.
#
# Query [0, 4] → Substring "10001" → Augmented to "1100011"
#
#         Because there is no block of '1's surrounded by '0's, no valid
# trade is possible. The maximum number of active sections is 2.
#
# Example 4:
#
# Input: s = "01010", queries = [[0,3],[1,4],[1,3]]
#
# Output: [4,4,2]
#
# Explanation:
#
# Query [0, 3] → Substring "0101" → Augmented to "101011"
#
#         Choose "010", convert "010" → "000" → "111".
#
#         The final string without augmentation is "11110". The maximum
# number of active sections is 4.
#
# Query [1, 4] → Substring "1010" → Augmented to "110101"
#
#         Choose "010", convert "010" → "000" → "111".
#
#         The final string without augmentation is "01111". The maximum
# number of active sections is 4.
#
# Query [1, 3] → Substring "101" → Augmented to "11011"
#
#         Because there is no block of '1's surrounded by '0's, no valid
# trade is possible. The maximum number of active sections is 2.
#
# Constraints:
#
# 1 <= n == s.length <= 10^5
#
# 1 <= queries.length <= 10^5
#
# s[i] is either '0' or '1'.
#
# queries[i] = [l_i, r_i]
#
# 0 <= l_i <= r_i < n
#

# @lc code=start
from typing import List
class SparseTable:
    def __init__(self, arr: List[int]):
        self.n = len(arr)
        if self.n == 0:
            self.st = []
            return
        k = self.n.bit_length()
        self.st = [arr[:]]
        for i in range(1, k):
            prev = self.st[i - 1]
            row = []
            span = 1 << (i - 1)
            for j in range(self.n - (1 << i) + 1):
                row.append(max(prev[j], prev[j + span]))
            self.st.append(row)

    def query(self, l: int, r: int) -> int:
        """
        Interview explanation:
        Sparse-table range maximum on inclusive [l, r].

        Algorithm:
        - Use precomputed power-of-two windows covering [l, r].

        Complexity: O(1) time after O(n log n) build.
        """
        i = (r - l + 1).bit_length() - 1
        return max(self.st[i][l], self.st[i][r - (1 << i) + 1])


class Solution:
    def maxActiveSectionsAfterTrade(self, s: str, queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        A trade removes a 1-block between two 0-blocks then flips the merged
        0-run to 1s; net gain equals the sum of those two 0-block lengths.
        Queries ask the same on a substring (augmented with virtual 1s), counted
        on the whole string: total ones + best local gain.

        Algorithm:
        - Compress zero-runs; precompute adjacent-run length sums.
        - Sparse table for range-max of adjacent sums.
        - Per query, take max of fully-inside adjacent pairs and boundary
          partial zero-runs clipped by [l, r].

        Complexity: O(n log n + q) time, O(n log n) space.
        """
        ones = s.count("1")
        groups: List[List[int]] = []  # [start, length]
        lookup = [0] * len(s)
        for i, ch in enumerate(s):
            if ch == "0":
                if i > 0 and s[i - 1] == "0":
                    groups[-1][1] += 1
                else:
                    groups.append([i, 1])
            lookup[i] = len(groups) - 1

        if not groups:
            return [ones] * len(queries)

        merges = [groups[i][1] + groups[i + 1][1] for i in range(len(groups) - 1)]
        st = SparseTable(merges)
        ans = []
        for l, r in queries:
            gl, gr = lookup[l], lookup[r]
            left_cnt = (
                groups[gl][1] - (l - groups[gl][0]) if gl != -1 else -1
            )
            right_cnt = r - groups[gr][0] + 1 if gr != -1 else -1
            # complete zero groups strictly inside (l, r] / [l, r)
            left = gl + 1
            right = gr - (1 if s[r] == "0" else 0)
            best = ones
            if left <= right - 1 and merges:
                best = max(best, ones + st.query(left, right - 1))
            if s[l] == "0" and s[r] == "0" and gl + 1 == gr:
                best = max(best, ones + left_cnt + right_cnt)
            if s[l] == "0" and gl + 1 <= right:
                best = max(best, ones + left_cnt + groups[gl + 1][1])
            if s[r] == "0" and left <= gr - 1:
                best = max(best, ones + right_cnt + groups[gr - 1][1])
            ans.append(best)
        return ans
# @lc code=end

