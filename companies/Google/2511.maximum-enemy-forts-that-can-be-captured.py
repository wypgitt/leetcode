#
# @lc app=leetcode id=2511 lang=python3
#
# [2511] Maximum Enemy Forts That Can Be Captured
#
# https://leetcode.com/problems/maximum-enemy-forts-that-can-be-captured/description/
#
# algorithms
# Easy (41.73%)
# Likes:    336
# Dislikes: 304
# Total Accepted:    36.4K
# Total Submissions: 87.3K
# Testcase Example:  "[1,0,0,-1,0,0,0,0,1]"
#
# You are given a 0-indexed integer array forts of length n representing the
# positions of several forts. forts[i] can be -1, 0, or 1 where:
#
#
# -1 represents there is no fort at the i^th position.
#
#
# 0 indicates there is an enemy fort at the i^th position.
#
#
# 1 indicates the fort at the i^th the position is under your command.
#
# Now you have decided to move your army from one of your forts at position i to
# an empty position j such that:
#
#
# 0 <= i, j <= n - 1
#
#
# The army travels over enemy forts only. Formally, for all k where min(i,j) < k
# < max(i,j), forts[k] == 0.
#
# While moving the army, all the enemy forts that come in the way are captured.
#
# Return the maximum number of enemy forts that can be captured. In case it is
# impossible to move your army, or you do not have any fort under your command,
# return 0.
#
#
#
# Example 1:
#
# Input: forts = [1,0,0,-1,0,0,0,0,1]
# Output: 4
# Explanation:
# - Moving the army from position 0 to position 3 captures 2 enemy forts, at 1
# and 2.
# - Moving the army from position 8 to position 3 captures 4 enemy forts.
# Since 4 is the maximum number of enemy forts that can be captured, we return
# 4.
#
# Example 2:
#
# Input: forts = [0,0,1,-1]
# Output: 0
# Explanation: Since no enemy fort can be captured, 0 is returned.
#
#
#
# Constraints:
#
#
# 1 <= forts.length <= 1000
#
#
# -1 <= forts[i] <= 1
#

# @lc code=start
from typing import List


class Solution:
    def captureForts(self, forts: List[int]) -> int:
        """
        Interview explanation:
        Move from a fort you command (1) to an empty slot (-1) over only enemy
        forts (0); maximize enemies captured (zeros between them).

        Algorithm:
        - One pass: remember last non-zero fort; when current is non-zero and
          opposite sign, update answer with zeros between them.

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        prev = -1
        for i, v in enumerate(forts):
            if v == 0:
                continue
            if prev != -1 and forts[prev] == -v:
                ans = max(ans, i - prev - 1)
            prev = i
        return ans
# @lc code=end
