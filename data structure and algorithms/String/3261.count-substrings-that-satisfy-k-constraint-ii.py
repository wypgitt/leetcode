#
# @lc app=leetcode id=3261 lang=python3
#
# [3261] Count Substrings That Satisfy K-Constraint II
#
# https://leetcode.com/problems/count-substrings-that-satisfy-k-constraint-ii/description/
#
# algorithms
# Hard (23.52%)
# Likes:    151
# Dislikes: 12
# Total Accepted:    6.3K
# Total Submissions: 26.6K
# Testcase Example:  "\"0001111\"\n2\n[[0,6]]"
#
#
# You are given a binary string s and an integer k.
#
# You are also given a 2D integer array queries, where queries[i] = [l_i,
# r_i].
#
# A binary string satisfies the k-constraint if either of the following
# conditions holds:
#
# The number of 0's in the string is at most k.
#
# The number of 1's in the string is at most k.
#
# Return an integer array answer, where answer[i] is the number of
# substrings of s[l_i..r_i] that satisfy the k-constraint.
#
# Example 1:
#
# Input: s = "0001111", k = 2, queries = [[0,6]]
#
# Output: [26]
#
# Explanation:
#
# For the query [0, 6], all substrings of s[0..6] = "0001111" satisfy the
# k-constraint except for the substrings s[0..5] = "000111" and s[0..6] =
# "0001111".
#
# Example 2:
#
# Input: s = "010101", k = 1, queries = [[0,5],[1,4],[2,3]]
#
# Output: [15,9,3]
#
# Explanation:
#
# The substrings of s with a length greater than 3 do not satisfy the
# k-constraint.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s[i] is either '0' or '1'.
#
# 1 <= k <= s.length
#
# 1 <= queries.length <= 10^5
#
# queries[i] == [l_i, r_i]
#
# 0 <= l_i <= r_i < s.length
#
# All queries are distinct.
#

# @lc code=start

from typing import List
from bisect import bisect_left


class Solution:
    def countKConstraintSubstrings(self, s: str, k: int, queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        A substring satisfies the k-constraint iff it has ≤k zeros or ≤k ones.
        For each right endpoint r, valid left endpoints form [left[r], r] where
        left[r] is nondecreasing. Answer range queries with prefix sums + binary search.

        Algorithm:
        - Two pointers: expand r; advance L while both zero and one counts exceed k.
        - left[r] = L. Prefetch pref[i] = sum_{j<i} (j - left[j] + 1).
        - For query [L,R], find first mid with left[mid] >= L; sum closed forms on
          [L,mid) and prefix on [mid,R].

        Complexity: O(n + q log n) time, O(n) space.
        """
        n = len(s)
        left = [0] * n
        zeros = ones = 0
        L = 0
        for r, ch in enumerate(s):
            if ch == '0':
                zeros += 1
            else:
                ones += 1
            while zeros > k and ones > k:
                if s[L] == '0':
                    zeros -= 1
                else:
                    ones -= 1
                L += 1
            left[r] = L

        # pref[i] = sum of (j - left[j] + 1) for j in 0..i-1
        # sumL[i] = sum of left[j] for j in 0..i-1
        # sumJ[i] = sum of j for j in 0..i-1
        pref = [0] * (n + 1)
        sum_left = [0] * (n + 1)
        sum_j = [0] * (n + 1)
        for j in range(n):
            pref[j + 1] = pref[j] + (j - left[j] + 1)
            sum_left[j + 1] = sum_left[j] + left[j]
            sum_j[j + 1] = sum_j[j] + j

        ans = []
        for Lq, Rq in queries:
            # first j in [Lq, Rq] with left[j] >= Lq
            mid = bisect_left(left, Lq, Lq, Rq + 1)
            total = 0
            if mid > Lq:
                # for j in [Lq, mid): contribute j - Lq + 1
                cnt = mid - Lq
                total += (sum_j[mid] - sum_j[Lq]) - Lq * cnt + cnt
            if mid <= Rq:
                total += pref[Rq + 1] - pref[mid]
            ans.append(total)
        return ans
# @lc code=end
