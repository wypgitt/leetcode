#
# @lc app=leetcode id=3184 lang=python3
#
# [3184] Count Pairs That Form a Complete Day I
#
# https://leetcode.com/problems/count-pairs-that-form-a-complete-day-i/description/
#
# algorithms
# Easy (78.34%)
# Likes:    172
# Dislikes: 12
# Total Accepted:    79K
# Total Submissions: 100.8K
# Testcase Example:  "[12,12,30,24,24]"
#
#
# Given an integer array hours representing times in hours, return an
# integer denoting the number of pairs i, j where i < j and hours[i] +
# hours[j] forms a complete day.
#
# A complete day is defined as a time duration that is an exact multiple
# of 24 hours.
#
# For example, 1 day is 24 hours, 2 days is 48 hours, 3 days is 72 hours,
# and so on.
#
# Example 1:
#
# Input: hours = [12,12,30,24,24]
#
# Output: 2
#
# Explanation:
#
# The pairs of indices that form a complete day are (0, 1) and (3, 4).
#
# Example 2:
#
# Input: hours = [72,48,24,3]
#
# Output: 3
#
# Explanation:
#
# The pairs of indices that form a complete day are (0, 1), (0, 2), and
# (1, 2).
#
# Constraints:
#
# 1 <= hours.length <= 100
#
# 1 <= hours[i] <= 10^9
#

# @lc code=start

from typing import List


class Solution:
    def countCompleteDayPairs(self, hours: List[int]) -> int:
        """
        Interview explanation:
        Pair i < j if hours[i]+hours[j] is a multiple of 24, i.e. residues
        r and (24-r)%24.

        Algorithm:
        - Brute force all pairs (n <= 100): check (a+b) % 24 == 0.

        Complexity: O(n^2) time, O(1) space.
        """
        n = len(hours)
        ans = 0
        for i in range(n):
            for j in range(i + 1, n):
                if (hours[i] + hours[j]) % 24 == 0:
                    ans += 1
        return ans

    def countCompleteDayPairs_modulo(self, hours: List[int]) -> int:
        """
        Interview explanation:
        Frequency of residues mod 24; each hour pairs with complement residue.

        Algorithm:
        - cnt[r] = count of hours % 24 == r.
        - For each hour, add cnt[(24 - r) % 24], then increment cnt[r].

        Complexity: O(n) time, O(1) space.
        """
        cnt = [0] * 24
        ans = 0
        for h in hours:
            r = h % 24
            ans += cnt[(24 - r) % 24]
            cnt[r] += 1
        return ans
# @lc code=end
