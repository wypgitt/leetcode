#
# @lc app=leetcode id=3181 lang=python3
#
# [3181] Maximum Total Reward Using Operations II
#
# https://leetcode.com/problems/maximum-total-reward-using-operations-ii/description/
#
# algorithms
# Hard (21.77%)
# Likes:    136
# Dislikes: 32
# Total Accepted:    8.9K
# Total Submissions: 41K
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
# 1 <= rewardValues.length <= 5 * 10^4
#
# 1 <= rewardValues[i] <= 5 * 10^4
#

# @lc code=start
from typing import List


class Solution:
    def maxTotalReward(self, rewardValues: List[int]) -> int:
        """
        Interview explanation:
        Same reward rule as I, but values up to 5e4. Python arbitrary-precision
        ints act as a fast bitset for achievable sums.

        Algorithm:
        - Unique-sort rewards; f bitset update: f |= (f & ((1<<v)-1)) << v.
        - Answer is the highest set bit index.

        Complexity: O(U * M / W) time, O(M / W) space (M < 2*max_reward).
        """
        vals = sorted(set(rewardValues))
        f = 1
        for v in vals:
            f |= (f & ((1 << v) - 1)) << v
        return f.bit_length() - 1

    def maxTotalReward_bound(self, rewardValues: List[int]) -> int:
        """
        Interview explanation:
        Alternate: note final answer is in [max, 2*max). Process ascending and
        only keep achievable sums strictly less than the next reward.

        Algorithm:
        - Same bitset; optionally early-stop when all sums < v are filled.

        Complexity: O(U * M / W) time, O(M / W) space.
        """
        vals = sorted(set(rewardValues))
        f = 1
        for v in vals:
            mask = (1 << v) - 1
            f |= (f & mask) << v
        return f.bit_length() - 1
# @lc code=end
