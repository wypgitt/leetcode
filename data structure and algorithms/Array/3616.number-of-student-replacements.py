#
# @lc app=leetcode id=3616 lang=python3
#
# [3616] Number of Student Replacements
#
# https://leetcode.com/problems/number-of-student-replacements/description/
#
# algorithms
# Medium (85.69%)
# Likes:    5
# Dislikes: 3
# Total Accepted:    1.1K
# Total Submissions: 1.3K
# Testcase Example:  "[4,1,2]"
#
#
# You are given an integer array ranks where ranks[i] represents the rank
# of the i^th student arriving in order. A lower number indicates a better
# rank.
#
# Initially, the first student is selected by default.
#
# A replacement occurs when a student with a strictly better rank arrives
# and replaces the current selection.
#
# Return the total number of replacements made.
#
# Example 1:
#
# Input: ranks = [4,1,2]
#
# Output: 1
#
# Explanation:
#
# The first student with ranks[0] = 4 is initially selected.
#
# The second student with ranks[1] = 1 is better than the current
# selection, so a replacement occurs.
#
# The third student has a worse rank, so no replacement occurs.
#
# Thus, the number of replacements is 1.
#
# Example 2:
#
# Input: ranks = [2,2,3]
#
# Output: 0
#
# Explanation:
#
# The first student with ranks[0] = 2 is initially selected.
#
# Neither of ranks[1] = 2 or ranks[2] = 3 is better than the current
# selection.
#
# Thus, the number of replacements is 0.
#
# Constraints:
#
# 1 <= ranks.length <= 10^5​​​​​​​
#
# 1 <= ranks[i] <= 10^5
#

# @lc code=start

from typing import List


class Solution:
    def totalReplacements(self, ranks: List[int]) -> int:
        """
        Interview explanation:
        First student is selected; each later strictly better (smaller) rank
        replaces the current selection. Count replacements.

        Algorithm:
        - Track running minimum; increment on each new strict minimum.

        Complexity: O(n) time, O(1) space.
        """
        best = ranks[0]
        replacements = 0
        for r in ranks[1:]:
            if r < best:
                replacements += 1
                best = r
        return replacements
# @lc code=end
