#
# @lc app=leetcode id=3687 lang=python3
#
# [3687] Library Late Fee Calculator
#
# https://leetcode.com/problems/library-late-fee-calculator/description/
#
# algorithms
# Easy (94.51%)
# Likes:    5
# Dislikes: 3
# Total Accepted:    2.4K
# Total Submissions: 2.5K
# Testcase Example:  "[5,1,7]"
#
#
# You are given an integer array daysLate where daysLate[i] indicates how
# many days late the i^th book was returned.
#
# The penalty is calculated as follows:
#
# If daysLate[i] == 1, penalty is 1.
#
# If 2 <= daysLate[i] <= 5, penalty is 2 * daysLate[i].
#
# If daysLate[i] > 5, penalty is 3 * daysLate[i].
#
# Return the total penalty for all books.
#
# Example 1:
#
# Input: daysLate = [5,1,7]
#
# Output: 32
#
# Explanation:
#
# daysLate[0] = 5: Penalty is 2 * daysLate[0] = 2 * 5 = 10.
#
# daysLate[1] = 1: Penalty is 1.
#
# daysLate[2] = 7: Penalty is 3 * daysLate[2] = 3 * 7 = 21.
#
# Thus, the total penalty is 10 + 1 + 21 = 32.
#
# Example 2:
#
# Input: daysLate = [1,1]
#
# Output: 2
#
# Explanation:
#
# daysLate[0] = 1: Penalty is 1.
#
# daysLate[1] = 1: Penalty is 1.
#
# Thus, the total penalty is 1 + 1 = 2.
#
# Constraints:
#
# 1 <= daysLate.length <= 100
#
# 1 <= daysLate[i] <= 100
#

# @lc code=start

from typing import List


class Solution:
    def lateFee(self, daysLate: List[int]) -> int:
        """
        Interview explanation:
        Apply the piecewise penalty rule per book and sum.

        Algorithm:
        - 1 day -> 1; 2..5 -> 2*d; else -> 3*d.

        Complexity: O(n) time, O(1) space.
        """
        total = 0
        for d in daysLate:
            if d == 1:
                total += 1
            elif d <= 5:
                total += 2 * d
            else:
                total += 3 * d
        return total
# @lc code=end
