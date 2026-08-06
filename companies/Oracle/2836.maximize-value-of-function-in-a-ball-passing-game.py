#
# @lc app=leetcode id=2836 lang=python3
#
# [2836] Maximize Value of Function in a Ball Passing Game
#
# https://leetcode.com/problems/maximize-value-of-function-in-a-ball-passing-game/description/
#
# algorithms
# Hard (31.73%)
# Likes:    323
# Dislikes: 93
# Total Accepted:    7.1K
# Total Submissions: 22.5K
# Testcase Example:  "[2,0,1]\n4"
#
#
# You are given an integer array receiver of length n and an integer k. n
# players are playing a ball-passing game.
#
# You choose the starting player, i. The game proceeds as follows: player
# i passes the ball to player receiver[i], who then passes it to
# receiver[receiver[i]], and so on, for k passes in total. The game's
# score is the sum of the indices of the players who touched the ball,
# including repetitions, i.e. i + receiver[i] + receiver[receiver[i]] +
# ... + receiver^(k)[i].
#
# Return the maximum possible score.
#
# Notes:
#
# receiver may contain duplicates.
#
# receiver[i] may be equal to i.
#
# Example 1:
#
# Input: receiver = [2,0,1], k = 4
#
# Output: 6
#
# Explanation:
#
# Starting with player i = 2 the initial score is 2:
#
#                         Pass
#                         Sender Index
#                         Receiver Index
#                         Score
#
#                         1
#                         2
#                         1
#                         3
#
#                         2
#                         1
#                         0
#                         3
#
#                         3
#                         0
#                         2
#                         5
#
#                         4
#                         2
#                         1
#                         6
#
# Example 2:
#
# Input: receiver = [1,1,1,2,3], k = 3
#
# Output: 10
#
# Explanation:
#
# Starting with player i = 4 the initial score is 4:
#
#                         Pass
#                         Sender Index
#                         Receiver Index
#                         Score
#
#                         1
#                         4
#                         3
#                         7
#
#                         2
#                         3
#                         2
#                         9
#
#                         3
#                         2
#                         1
#                         10
#
# Constraints:
#
# 1 <= receiver.length == n <= 10^5
#
# 0 <= receiver[i] <= n - 1
#
# 1 <= k <= 10^10
#

# @lc code=start
from typing import List


class Solution:
    def getMaxFunctionValue(self, receiver: List[int], k: int) -> int:
        """
        Interview explanation:
        From start i, after k passes the score is sum of i and the k receivers.
        Functional graph; maximize over start. k up to 1e10 => binary lifting.

        Algorithm:
        - up[j][i] = node after 2^j passes; sm[j][i] = sum of those 2^j nodes.
        - For each start, walk bits of k adding sm contributions plus start itself.

        Complexity: O(n log k) time and space.
        """
        n = len(receiver)
        m = k.bit_length() + 1
        up = [[0] * n for _ in range(m)]
        sm = [[0] * n for _ in range(m)]
        for i in range(n):
            up[0][i] = receiver[i]
            sm[0][i] = receiver[i]
        for j in range(1, m):
            for i in range(n):
                mid = up[j - 1][i]
                up[j][i] = up[j - 1][mid]
                sm[j][i] = sm[j - 1][i] + sm[j - 1][mid]

        ans = 0
        for i in range(n):
            cur = i
            total = i
            steps = k
            bit = 0
            while steps:
                if steps & 1:
                    total += sm[bit][cur]
                    cur = up[bit][cur]
                steps >>= 1
                bit += 1
            ans = max(ans, total)
        return ans
# @lc code=end
