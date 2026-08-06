#
# @lc app=leetcode id=2410 lang=python3
#
# [2410] Maximum Matching of Players With Trainers
#
# https://leetcode.com/problems/maximum-matching-of-players-with-trainers/description/
#
# algorithms
# Medium (75.45%)
# Likes:    948
# Dislikes: 35
# Total Accepted:    192.7K
# Total Submissions: 255.4K
# Testcase Example:  "[4,7,9]\n[8,2,5,8]"
#
# You are given a 0-indexed integer array players, where players[i] represents
# the ability of the i^th player. You are also given a 0-indexed integer array
# trainers, where trainers[j] represents the training capacity of the j^th
# trainer.
#
# The i^th player can match with the j^th trainer if the player's ability is
# less than or equal to the trainer's training capacity. Additionally, the i^th
# player can be matched with at most one trainer, and the j^th trainer can be
# matched with at most one player.
#
# Return the maximum number of matchings between players and trainers that
# satisfy these conditions.
#
#
#
# Example 1:
#
# Input: players = [4,7,9], trainers = [8,2,5,8]
# Output: 2
# Explanation:
# One of the ways we can form two matchings is as follows:
# - players[0] can be matched with trainers[0] since 4 <= 8.
# - players[1] can be matched with trainers[3] since 7 <= 8.
# It can be proven that 2 is the maximum number of matchings that can be formed.
#
# Example 2:
#
# Input: players = [1,1,1], trainers = [10]
# Output: 1
# Explanation:
# The trainer can be matched with any of the 3 players.
# Each player can only be matched with one trainer, so the maximum answer is 1.
#
#
#
# Constraints:
#
#
# 1 <= players.length, trainers.length <= 10^5
#
#
# 1 <= players[i], trainers[j] <= 10^9
#
#
#
# Note: This question is the same as  445: Assign Cookies.
#

# @lc code=start
from typing import List


class Solution:
    def matchPlayersAndTrainers(self, players: List[int], trainers: List[int]) -> int:
        """
        Interview explanation:
        Match player to trainer if ability <= training capacity; maximize matches
        (each used once).

        Algorithm:
        - Sort both; two pointers greedily assign smallest feasible trainer.

        Complexity: O(n log n + m log m) time, O(1) extra space.
        """
        players.sort()
        trainers.sort()
        i = j = 0
        while i < len(players) and j < len(trainers):
            if players[i] <= trainers[j]:
                i += 1
            j += 1
        return i

    def matchPlayersAndTrainers_two_pointers(
        self, players: List[int], trainers: List[int]
    ) -> int:
        """
        Interview explanation:
        Alternate identical greedy with explicit match counter.

        Algorithm:
        - Sort; advance trainer pointer; count when player fits.

        Complexity: O(n log n + m log m) time, O(1) space.
        """
        players.sort()
        trainers.sort()
        ans = 0
        j = 0
        m = len(trainers)
        for p in players:
            while j < m and trainers[j] < p:
                j += 1
            if j == m:
                break
            ans += 1
            j += 1
        return ans
# @lc code=end
