#
# @lc app=leetcode id=319 lang=python3
#
# [319] Bulb Switcher
#
# https://leetcode.com/problems/bulb-switcher/description/
#
# algorithms
# Medium (56.26%)
# Likes:    2989
# Dislikes: 3246
# Total Accepted:    321K
# Total Submissions: 571K
# Testcase Example:  "3"
#
# There are n bulbs that are initially off. You first turn on all the bulbs,
# then you turn off every second bulb.
#
# On the third round, you toggle every third bulb (turning on if it's off or
# turning off if it's on). For the i^th round, you toggle every i bulb. For the
# n^th round, you only toggle the last bulb.
#
# Return the number of bulbs that are on after n rounds.
#
# Example 1:
#
# Input: n = 3
# Output: 1
# Explanation: At first, the three bulbs are [off, off, off].
# After the first round, the three bulbs are [on, on, on].
# After the second round, the three bulbs are [on, off, on].
# After the third round, the three bulbs are [on, off, off].
# So you should return 1 because there is only one bulb is on.
#
# Example 2:
#
# Input: n = 0
# Output: 0
#
# Example 3:
#
# Input: n = 1
# Output: 1
#
# Constraints:
#
# 0 <= n <= 10^9
#

# @lc code=start
from math import isqrt


class Solution:
    def bulbSwitch(self, n: int) -> int:
        """
        Interview explanation:
        Bulb i ends on iff it has an odd number of factors, i.e. i is a perfect
        square. Count of on bulbs = floor(sqrt(n)).

        Complexity: O(1).
        """
        return isqrt(n)
# @lc code=end

