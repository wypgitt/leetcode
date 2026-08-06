#
# @lc app=leetcode id=3180 lang=python3
#
# [3180] Maximum Total Reward Using Operations I
#
# https://leetcode.com/problems/maximum-total-reward-using-operations-i/description/
#
# algorithms
# Medium (30.97%)
# Likes:    221
# Dislikes: 18
# Total Accepted:    31.8K
# Total Submissions: 102.8K
# Testcase Example:  "[1,1,3,3]"
#
#
# You are given an integer array rewardValues of length n, representing
# the values of rewards.
#
# Initially, your total reward x is 0, and all indices are unmarked. You
# are allowed to perform the following operation any number of times:
#
# Choose an unmarked index i from the range [0, n - 1].
#
# If rewardValues[i] is greater than your current total reward x, then add
# rewardValues[i] to x (i.e., x = x + rewardValues[i]), and mark the index
# i.
#
# Return an integer denoting the maximum total reward you can collect by
# performing the operations optimally.
#
# Example 1:
#
# Input: rewardValues = [1,1,3,3]
#
# Output: 4
#
# Explanation:
#
# During the operations, we can choose to mark the indices 0 and 2 in
# order, and the total reward will be 4, which is the maximum.
#
# Example 2:
#
# Input: rewardValues = [1,6,4,3,2]
#
# Output: 11
#
# Explanation:
#
# Mark the indices 0, 2, and 1 in order. The total reward will then be 11,
# which is the maximum.
#
# Constraints:
#
# 1 <= rewardValues.length <= 2000
#
# 1 <= rewardValues[i] <= 2000
#

# @lc code=start
from typing import List


class Solution:
    def maxTotalReward(self, rewardValues: List[int]) -> int:
        """
        Interview explanation:
        You may add a reward r only if current sum x < r. Optimal to consider
        distinct rewards in increasing order; achievable sums form a bitset.

        Algorithm:
        - Sort unique rewards. Bit i set <=> sum i achievable (start with 0).
        - For reward v: f |= (f & ((1<<v)-1)) << v.

        Complexity: O(U * M / W) bitset time (M <= 2*max), O(M/W) space.
        """
        vals = sorted(set(rewardValues))
        f = 1
        for v in vals:
            f |= (f & ((1 << v) - 1)) << v
        return f.bit_length() - 1

    def maxTotalReward_bool(self, rewardValues: List[int]) -> int:
        """
        Interview explanation:
        Alternate boolean DP: achievable[x] means sum x is reachable; update
        high-to-low style via a fresh set of new sums per reward.

        Algorithm:
        - For each v ascending, for each achievable x < v mark x+v.

        Complexity: O(U * M) time, O(M) space.
        """
        vals = sorted(set(rewardValues))
        mx = vals[-1]
        achievable = [False] * (2 * mx)
        achievable[0] = True
        ans = 0
        for v in vals:
            for x in range(v):
                if achievable[x]:
                    nxt = x + v
                    achievable[nxt] = True
                    ans = max(ans, nxt)
        return ans
# @lc code=end
