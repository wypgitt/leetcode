#
# @lc app=leetcode id=3784 lang=python3
#
# [3784] Minimum Deletion Cost to Make All Characters Equal
#
# https://leetcode.com/problems/minimum-deletion-cost-to-make-all-characters-equal/description/
#
# algorithms
# Medium (55.34%)
# Likes:    92
# Dislikes: 11
# Total Accepted:    37.6K
# Total Submissions: 67.9K
# Testcase Example:  "\"aabaac\"\n[1,2,3,4,1,10]"
#
#
# You are given a string s of length n and an integer array cost of the
# same length, where cost[i] is the cost to delete the i^th character of
# s.
#
# You may delete any number of characters from s (possibly none), such
# that the resulting string is non-empty and consists of equal characters.
#
# Return an integer denoting the minimum total deletion cost required.
#
# Example 1:
#
# Input: s = "aabaac", cost = [1,2,3,4,1,10]
#
# Output: 11
#
# Explanation:
#
# Deleting the characters at indices 0, 1, 2, 3, 4 results in the string
# "c", which consists of equal characters, and the total cost is cost[0] +
# cost[1] + cost[2] + cost[3] + cost[4] = 1 + 2 + 3 + 4 + 1 = 11.
#
# Example 2:
#
# Input: s = "abc", cost = [10,5,8]
#
# Output: 13
#
# Explanation:
#
# Deleting the characters at indices 1 and 2 results in the string "a",
# which consists of equal characters, and the total cost is cost[1] +
# cost[2] = 5 + 8 = 13.
#
# Example 3:
#
# Input: s = "zzzzz", cost = [67,67,67,67,67]
#
# Output: 0
#
# Explanation:
#
# All characters in s are equal, so the deletion cost is 0.
#
# Constraints:
#
# n == s.length == cost.length
#
# 1 <= n <= 10^5
#
# 1 <= cost[i] <= 10^9
#
# s consists of lowercase English letters.
#

# @lc code=start
from typing import List


class Solution:
    def minCost(self, s: str, cost: List[int]) -> int:
        """
        Interview explanation:
        Keep one letter c and delete everything else. Optimal c maximizes the
        total cost of kept occurrences; answer is total_cost - that max.

        Algorithm:
        - Sum cost per character; return sum(cost) - max(per-char sums).

        Complexity: O(n) time, O(1) space (26 letters).
        """
        total = sum(cost)
        best = [0] * 26
        for ch, c in zip(s, cost):
            best[ord(ch) - 97] += c
        return total - max(best)

    def minCost_counter(self, s: str, cost: List[int]) -> int:
        """
        Interview explanation:
        Alternate: dict accumulation of keep-cost per character.

        Algorithm:
        - Same identity: min delete = total - max keep.

        Complexity: O(n) time, O(1) space.
        """
        from collections import defaultdict
        keep = defaultdict(int)
        total = 0
        for ch, c in zip(s, cost):
            keep[ch] += c
            total += c
        return total - max(keep.values())
# @lc code=end
