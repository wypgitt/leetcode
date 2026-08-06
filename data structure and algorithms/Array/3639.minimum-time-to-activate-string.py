#
# @lc app=leetcode id=3639 lang=python3
#
# [3639] Minimum Time to Activate String
#
# https://leetcode.com/problems/minimum-time-to-activate-string/description/
#
# algorithms
# Medium (49.26%)
# Likes:    125
# Dislikes: 6
# Total Accepted:    35.7K
# Total Submissions: 72.4K
# Testcase Example:  "\"abc\"\n[1,0,2]\n2"
#
#
# You are given a string s of length n and an integer array order, where
# order is a permutation of the numbers in the range [0, n - 1].
#
# Starting from time t = 0, replace the character at index order[t] in s
# with '*' at each time step.
#
# A substring is valid if it contains at least one '*'.
#
# A string is active if the total number of valid substrings is greater
# than or equal to k.
#
# Return the minimum time t at which the string s becomes active. If it is
# impossible, return -1.
#
# Example 1:
#
# Input: s = "abc", order = [1,0,2], k = 2
#
# Output: 0
#
# Explanation:
#
#                         t
#                         order[t]
#                         Modified s
#                         Valid Substrings
#                         Count
#                         Active
#
#                         (Count >= k)
#
#                         0
#                         1
#                         "a*c"
#                         "*", "a*", "*c", "a*c"
#                         4
#                         Yes
#
# The string s becomes active at t = 0. Thus, the answer is 0.
#
# Example 2:
#
# Input: s = "cat", order = [0,2,1], k = 6
#
# Output: 2
#
# Explanation:
#
#                         t
#                         order[t]
#                         Modified s
#                         Valid Substrings
#                         Count
#                         Active
#
#                         (Count >= k)
#
#                         0
#                         0
#                         "*at"
#                         "*", "*a", "*at"
#                         3
#                         No
#
#                         1
#                         2
#                         "*a*"
#                         "*", "*a", "*a*", "a*", "*"
#                         5
#                         No
#
#                         2
#                         1
#                         "***"
#                         All substrings (contain '*')
#                         6
#                         Yes
#
# The string s becomes active at t = 2. Thus, the answer is 2.
#
# Example 3:
#
# Input: s = "xy", order = [0,1], k = 4
#
# Output: -1
#
# Explanation:
#
# Even after all replacements, it is impossible to obtain k = 4 valid
# substrings. Thus, the answer is -1.
#
# Constraints:
#
# 1 <= n == s.length <= 10^5
#
# order.length == n
#
# 0 <= order[i] <= n - 1
#
# s consists of lowercase English letters.
#
# order is a permutation of integers from 0 to n - 1.
#
# 1 <= k <= 10^9
#

# @lc code=start

from typing import List


class Solution:
    def minTime(self, s: str, order: List[int], k: int) -> int:
        """
        Interview explanation:
        After starring positions order[0..t], count substrings containing at
        least one '*'. Total substrings = n(n+1)/2; invalid ones lie in gaps
        between stars. Binary search on t works, but a reverse simulation is
        linear: start from all starred and undo stars from the end.

        Algorithm:
        - If n(n+1)/2 < k return -1.
        - Doubly link indices; cnt starts as all substrings.
        - For t from n-1 down to 0: unstar order[t], subtract (i-L)*(R-i)
          newly invalidated substrings; if cnt < k, return t.

        Complexity: O(n) time, O(n) space.
        """
        n = len(s)
        left = list(range(-1, n - 1))
        right = list(range(1, n + 1))
        cnt = n * (n + 1) // 2
        if cnt < k:
            return -1
        for t in range(n - 1, -1, -1):
            i = order[t]
            l, r = left[i], right[i]
            cnt -= (i - l) * (r - i)
            if cnt < k:
                return t
            if l >= 0:
                right[l] = r
            if r < n:
                left[r] = l
        return -1
# @lc code=end

