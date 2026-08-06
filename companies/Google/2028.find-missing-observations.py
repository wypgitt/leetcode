#
# @lc app=leetcode id=2028 lang=python3
#
# [2028] Find Missing Observations
#
# https://leetcode.com/problems/find-missing-observations/description/
#
# algorithms
# Medium (57.37%)
# Likes:    1131
# Dislikes: 108
# Total Accepted:    176K
# Total Submissions: 306.7K
# Testcase Example:  "[3,2,4,3]\n4\n2"
#
# You have observations of n + m 6-sided dice rolls with each face numbered from
# 1 to 6. n of the observations went missing, and you only have the observations
# of m rolls. Fortunately, you have also calculated the average value of the n +
# m rolls.
#
# You are given an integer array rolls of length m where rolls[i] is the value
# of the i^th observation. You are also given the two integers mean and n.
#
# Return an array of length n containing the missing observations such that the
# average value of the n + m rolls is exactly mean. If there are multiple valid
# answers, return any of them. If no such array exists, return an empty array.
#
# The average value of a set of k numbers is the sum of the numbers divided by
# k.
#
# Note that mean is an integer, so the sum of the n + m rolls should be
# divisible by n + m.
#
#
#
# Example 1:
#
# Input: rolls = [3,2,4,3], mean = 4, n = 2
# Output: [6,6]
# Explanation: The mean of all n + m rolls is (3 + 2 + 4 + 3 + 6 + 6) / 6 = 4.
#
# Example 2:
#
# Input: rolls = [1,5,6], mean = 3, n = 4
# Output: [2,3,2,2]
# Explanation: The mean of all n + m rolls is (1 + 5 + 6 + 2 + 3 + 2 + 2) / 7 =
# 3.
#
# Example 3:
#
# Input: rolls = [1,2,3,4], mean = 6, n = 4
# Output: []
# Explanation: It is impossible for the mean to be 6 no matter what the 4
# missing rolls are.
#
#
#
# Constraints:
#
#
# m == rolls.length
#
#
# 1 <= n, m <= 10^5
#
#
# 1 <= rolls[i], mean <= 6
#

# @lc code=start
from typing import List


class Solution:
    def missingRolls(self, rolls: List[int], mean: int, n: int) -> List[int]:
        """
        Interview explanation:
        n missing dice (1..6) so that mean of all m+n rolls equals mean.

        Algorithm:
        - Need sum = mean*(m+n) - sum(rolls). If not in [n, 6n] return [].
        - Distribute base = sum//n, give +1 to first sum%n dice.

        Complexity: O(m+n) time, O(n) space.
        """
        m = len(rolls)
        total = mean * (m + n) - sum(rolls)
        if total < n or total > 6 * n:
            return []
        q, r = divmod(total, n)
        return [q + 1] * r + [q] * (n - r)
# @lc code=end
