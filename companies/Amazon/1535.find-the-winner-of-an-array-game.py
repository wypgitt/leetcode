#
# @lc app=leetcode id=1535 lang=python3
#
# [1535] Find the Winner of an Array Game
#
# https://leetcode.com/problems/find-the-winner-of-an-array-game/description/
#
# algorithms
# Medium (56.86%)
# Likes:    1629
# Dislikes: 88
# Total Accepted:    129K
# Total Submissions: 226K
# Testcase Example:  "[2,1,3,5,4,6,7]"
#
# Given an integer array arr of distinct integers and an integer k.
#
# A game will be played between the first two elements of the array (i.e.
# arr[0] and arr[1]). In each round of the game, we compare arr[0] with arr[1],
# the larger integer wins and remains at position 0, and the smaller integer
# moves to the end of the array. The game ends when an integer wins k
# consecutive rounds.
#
# Return the integer which will win the game.
#
# It is guaranteed that there will be a winner of the game.
#
# Example 1:
#
# Input: arr = [2,1,3,5,4,6,7], k = 2
# Output: 5
# Explanation: Let's see the rounds of the game:
# Round | arr | winner | win_count
# 1 | [2,1,3,5,4,6,7] | 2 | 1
# 2 | [2,3,5,4,6,7,1] | 3 | 1
# 3 | [3,5,4,6,7,1,2] | 5 | 1
# 4 | [5,4,6,7,1,2,3] | 5 | 2
# So we can see that 4 rounds will be played and 5 is the winner because it
# wins 2 consecutive games.
#
# Example 2:
#
# Input: arr = [3,2,1], k = 10
# Output: 3
# Explanation: 3 will win the first 10 rounds consecutively.
#
# Constraints:
#
# 2 <= arr.length <= 10^5
#
# 1 <= arr[i] <= 10^6
#
# arr contains distinct integers.
#
# 1 <= k <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def getWinner(self, arr: List[int], k: int) -> int:
        """
        Interview explanation:
        Array game: compare first two; larger wins, smaller goes to end. First
        to win k consecutive comparisons wins. Equivalent: scan for first
        element that beats next k elements (or global max if k large).

        Algorithm:
        - cur=arr[0], streak=0; for x in arr[1:]: if cur>x streak++ else
          cur=x,streak=1; if streak==k return cur. Also if k>=n-1 return max.

        Complexity: O(n) time, O(1) space.
        """
        if k >= len(arr) - 1:
            return max(arr)
        cur = arr[0]
        streak = 0
        for i in range(1, len(arr)):
            if cur > arr[i]:
                streak += 1
            else:
                cur = arr[i]
                streak = 1
            if streak == k:
                return cur
        return cur

    def getWinner_deque(self, arr: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate direct simulation with a deque (faithful to the game rules).
        Cap rounds: winner is at most the global max after one full pass.

        Algorithm:
        - deque(arr); streak=0; while streak<k: pop first two, push loser back.

        Complexity: O(n) time (streak resets bound comparisons), O(n) space.
        """
        from collections import deque

        if k >= len(arr) - 1:
            return max(arr)
        q = deque(arr)
        streak = 0
        cur = q.popleft()
        while streak < k:
            nxt = q.popleft()
            if cur > nxt:
                q.append(nxt)
                streak += 1
            else:
                q.append(cur)
                cur = nxt
                streak = 1
        return cur
# @lc code=end
