#
# @lc app=leetcode id=3185 lang=python3
#
# [3185] Count Pairs That Form a Complete Day II
#
# https://leetcode.com/problems/count-pairs-that-form-a-complete-day-ii/description/
#
# algorithms
# Medium (43.97%)
# Likes:    202
# Dislikes: 12
# Total Accepted:    49.9K
# Total Submissions: 113.4K
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
# Explanation: The pairs of indices that form a complete day are (0, 1)
# and (3, 4).
#
# Example 2:
#
# Input: hours = [72,48,24,3]
#
# Output: 3
#
# Explanation: The pairs of indices that form a complete day are (0, 1),
# (0, 2), and (1, 2).
#
# Constraints:
#
# 1 <= hours.length <= 5 * 10^5
#
# 1 <= hours[i] <= 10^9
#

# @lc code=start

from typing import List


class Solution:
    def countCompleteDayPairs(self, hours: List[int]) -> int:
        """
        Interview explanation:
        Same as Complete Day I but n up to 5e5: count pairs whose hours sum
        to a multiple of 24 via residue frequencies.

        Algorithm:
        - Maintain cnt[0..23]. For residue r, add cnt[(24-r)%24], then cnt[r]++.

        Complexity: O(n) time, O(1) space.
        """
        cnt = [0] * 24
        ans = 0
        for h in hours:
            r = h % 24
            ans += cnt[(24 - r) % 24]
            cnt[r] += 1
        return ans

    def countCompleteDayPairs_formula(self, hours: List[int]) -> int:
        """
        Interview explanation:
        Two-pass residue counts: pairs within 0, within 12, and across r/(24-r).

        Algorithm:
        - Count all residues; ans = C(c0,2)+C(c12,2)+sum_r c[r]*c[24-r] for r=1..11.

        Complexity: O(n) time, O(1) space.
        """
        cnt = [0] * 24
        for h in hours:
            cnt[h % 24] += 1
        ans = cnt[0] * (cnt[0] - 1) // 2 + cnt[12] * (cnt[12] - 1) // 2
        for r in range(1, 12):
            ans += cnt[r] * cnt[24 - r]
        return ans
# @lc code=end
