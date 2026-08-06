#
# @lc app=leetcode id=1563 lang=python3
#
# [1563] Stone Game V
#
# https://leetcode.com/problems/stone-game-v/description/
#
# algorithms
# Hard (42.44%)
# Likes:    706
# Dislikes: 90
# Total Accepted:    28.2K
# Total Submissions: 66.5K
# Testcase Example:  "[6,2,3,4,5,5]"
#
# There are several stones arranged in a row, and each stone has an associated
# value which is an integer given in the array stoneValue.
#
# In each round of the game, Alice divides the row into two non-empty rows
# (i.e. left row and right row), then Bob calculates the value of each row
# which is the sum of the values of all the stones in this row. Bob throws away
# the row which has the maximum value, and Alice's score increases by the value
# of the remaining row. If the value of the two rows are equal, Bob lets Alice
# decide which row will be thrown away. The next round starts with the
# remaining row.
#
# The game ends when there is only one stone remaining. Alice's score is
# initially zero.
#
# Return the maximum score that Alice can obtain.
#
# Example 1:
#
# Input: stoneValue = [6,2,3,4,5,5]
# Output: 18
# Explanation: In the first round, Alice divides the row to [6,2,3], [4,5,5].
# The left row has the value 11 and the right row has value 14. Bob throws away
# the right row and Alice's score is now 11.
# In the second round Alice divides the row to [6], [2,3]. This time Bob throws
# away the left row and Alice's score becomes 16 (11 + 5).
# The last round Alice has only one choice to divide the row which is [2], [3].
# Bob throws away the right row and Alice's score is now 18 (16 + 2). The game
# ends because only one stone is remaining in the row.
#
# Example 2:
#
# Input: stoneValue = [7,7,7,7,7,7,7]
# Output: 28
#
# Example 3:
#
# Input: stoneValue = [4]
# Output: 0
#
# Constraints:
#
# 1 <= stoneValue.length <= 500
#
# 1 <= stoneValue[i] <= 10^6
#

# @lc code=start
from typing import List
from functools import lru_cache


class Solution:
    def stoneGameV(self, stoneValue: List[int]) -> int:
        """
        Interview explanation:
        Split subarray into left/right non-empty; discard larger sum side (or
        either if equal); score += remaining sum; recurse. Maximize Alice score.
        Interval DP with prefix sums; for each split compare left/right sums.

        Algorithm (DP):
        - pref prefix sums; dp(l,r)=max score on stoneValue[l:r].
        - For mid in (l,r): left=pref[mid]-pref[l], right=pref[r]-pref[mid].
          if left<right: cand=left+dp(l,mid); elif left>right: right+dp(mid,r);
          else max(left+dp(l,mid), right+dp(mid,r)).

        Complexity: O(n^3) time, O(n^2) space (n<=500).
        """
        n = len(stoneValue)
        pref = [0] * (n + 1)
        for i, v in enumerate(stoneValue):
            pref[i + 1] = pref[i] + v

        @lru_cache(None)
        def dp(l: int, r: int) -> int:
            if r - l <= 1:
                return 0
            best = 0
            for mid in range(l + 1, r):
                left = pref[mid] - pref[l]
                right = pref[r] - pref[mid]
                if left < right:
                    best = max(best, left + dp(l, mid))
                elif left > right:
                    best = max(best, right + dp(mid, r))
                else:
                    best = max(best, left + dp(l, mid), right + dp(mid, r))
            return best

        return dp(0, n)
# @lc code=end

