#
# @lc app=leetcode id=403 lang=python3
#
# [403] Frog Jump
#
# https://leetcode.com/problems/frog-jump/description/
#
# algorithms
# Hard (47.52%)
# Likes:    6060
# Dislikes: 280
# Total Accepted:    353K
# Total Submissions: 743K
# Testcase Example:  "[0,1,3,5,6,8,12,17]"
#
# A frog is crossing a river. The river is divided into some number of units,
# and at each unit, there may or may not exist a stone. The frog can jump on a
# stone, but it must not jump into the water.
#
# Given a list of stones positions (in units) in sorted ascending order,
# determine if the frog can cross the river by landing on the last stone.
# Initially, the frog is on the first stone and assumes the first jump must be
# 1 unit.
#
# If the frog's last jump was k units, its next jump must be either k - 1, k,
# or k + 1 units. The frog can only jump in the forward direction.
#
# Example 1:
#
# Input: stones = [0,1,3,5,6,8,12,17]
# Output: true
# Explanation: The frog can jump to the last stone by jumping 1 unit to the 2nd
# stone, then 2 units to the 3rd stone, then 2 units to the 4th stone, then 3
# units to the 6th stone, 4 units to the 7th stone, and 5 units to the 8th
# stone.
#
# Example 2:
#
# Input: stones = [0,1,2,3,4,8,9,11]
# Output: false
# Explanation: There is no way to jump to the last stone as the gap between the
# 5th and 6th stone is too large.
#
# Constraints:
#
# 2 <= stones.length <= 2000
#
# 0 <= stones[i] <= 2^31 - 1
#
# stones[0] == 0
#
# stones is sorted in a strictly increasing order.
#

# @lc code=start

from typing import List, Set


class Solution:
    def canCross(self, stones: List[int]) -> bool:
        """
        Interview explanation:
        DP with sets: for each stone, store jump sizes that can land there.
        From (pos, jump j) try next = pos+j-1, pos+j, pos+j+1 if those stones exist.

        Algorithm:
        - Map stone -> set of jumps that reach it; start {0: {0}}.
        - For each stone in order, for each j in its set, try j-1,j,j+1 > 0.
        - Success if last stone's set is non-empty.

        Complexity: O(n^2) time/space in worst case.
        """
        if stones[1] != 1:
            return False
        pos = {s: set() for s in stones}
        pos[0].add(0)
        stone_set = set(stones)
        for s in stones:
            for j in pos[s]:
                for nj in (j - 1, j, j + 1):
                    if nj > 0 and s + nj in stone_set:
                        pos[s + nj].add(nj)
        return bool(pos[stones[-1]])

    def canCrossDFS(self, stones: List[int]) -> bool:
        """
        Interview explanation:
        Alternate: DFS + memo on (index, last_jump). Same transition rules;
        prune with memoized failures/successes.

        Algorithm:
        - stone index map; dfs(i, k) tries next stones with jump in {k-1,k,k+1}.

        Complexity: O(n^2) time/space with memo.
        """
        n = len(stones)
        idx = {s: i for i, s in enumerate(stones)}
        memo = {}

        def dfs(i: int, k: int) -> bool:
            if i == n - 1:
                return True
            key = (i, k)
            if key in memo:
                return memo[key]
            for nj in (k - 1, k, k + 1):
                if nj > 0:
                    nxt = stones[i] + nj
                    if nxt in idx and dfs(idx[nxt], nj):
                        memo[key] = True
                        return True
            memo[key] = False
            return False

        return stones[1] == 1 and dfs(1, 1)
# @lc code=end
