#
# @lc app=leetcode id=1815 lang=python3
#
# [1815] Maximum Number of Groups Getting Fresh Donuts
#
# https://leetcode.com/problems/maximum-number-of-groups-getting-fresh-donuts/description/
#
# algorithms
# Hard (41.5%)
# Likes:    362
# Dislikes: 34
# Total Accepted:    8.8K
# Total Submissions: 21.2K
# Testcase Example:  "3"
#
# There is a donuts shop that bakes donuts in batches of batchSize. They have a
# rule where they must serve all of the donuts of a batch before serving any
# donuts of the next batch. You are given an integer batchSize and an integer
# array groups, where groups[i] denotes that there is a group of groups[i]
# customers that will visit the shop. Each customer will get exactly one donut.
#
# When a group visits the shop, all customers of the group must be served
# before serving any of the following groups. A group will be happy if they all
# get fresh donuts. That is, the first customer of the group does not receive a
# donut that was left over from the previous group.
#
# You can freely rearrange the ordering of the groups. Return the maximum
# possible number of happy groups after rearranging the groups.
#
# Example 1:
#
# Input: batchSize = 3, groups = [1,2,3,4,5,6]
# Output: 4
# Explanation: You can arrange the groups as [6,2,4,5,1,3]. Then the 1^st,
# 2^nd, 4^th, and 6^th groups will be happy.
#
# Example 2:
#
# Input: batchSize = 4, groups = [1,3,2,5,2,2,1,6]
# Output: 4
#
# Constraints:
#
# 1 <= batchSize <= 9
#
# 1 <= groups.length <= 30
#
# 1 <= groups[i] <= 10^9
#

# @lc code=start
from typing import List
from functools import lru_cache


class Solution:
    def maxHappyGroups(self, batchSize: int, groups: List[int]) -> int:
        """
        Interview explanation:
        Order groups to maximize how many start when leftover (sum%batchSize)==0.
        State DP over counts of each remainder and current leftover.

        Algorithm (memo DFS on remainder counts):
        - Count rem frequencies; rem 0 groups always happy.
        - dfs(state, left): try take each rem>0; add 1 if left==0; recurse.

        Complexity: O(batchSize * product(cnt_r+1)) time/space.
        """
        cnt = [0] * batchSize
        base = 0
        for g in groups:
            r = g % batchSize
            if r == 0:
                base += 1
            else:
                cnt[r] += 1

        @lru_cache(None)
        def dfs(state: tuple, left: int) -> int:
            st = list(state)
            best = 0
            for r in range(1, batchSize):
                if st[r] == 0:
                    continue
                st[r] -= 1
                add = 1 if left == 0 else 0
                best = max(best, add + dfs(tuple(st), (left + r) % batchSize))
                st[r] += 1
            return best

        return base + dfs(tuple(cnt), 0)
# @lc code=end
