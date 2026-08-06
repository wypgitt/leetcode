#
# @lc app=leetcode id=752 lang=python3
#
# [752] Open the Lock
#
# https://leetcode.com/problems/open-the-lock/description/
#
# algorithms
# Medium (61.48%)
# Likes:    5187
# Dislikes: 240
# Total Accepted:    420K
# Total Submissions: 683K
# Testcase Example:  "[\"0201\",\"0101\",\"0102\",\"1212\",\"2002\"]"
#
# You have a lock in front of you with 4 circular wheels. Each wheel has 10
# slots: '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'. The wheels can
# rotate freely and wrap around: for example we can turn '9' to be '0', or '0'
# to be '9'. Each move consists of turning one wheel one slot.
#
# The lock initially starts at '0000', a string representing the state of the 4
# wheels.
#
# You are given a list of deadends dead ends, meaning if the lock displays any
# of these codes, the wheels of the lock will stop turning and you will be
# unable to open it.
#
# Given a target representing the value of the wheels that will unlock the
# lock, return the minimum total number of turns required to open the lock, or
# -1 if it is impossible.
#
# Example 1:
#
# Input: deadends = ["0201","0101","0102","1212","2002"], target = "0202"
# Output: 6
# Explanation:
# A sequence of valid moves would be "0000" -> "1000" -> "1100" -> "1200" ->
# "1201" -> "1202" -> "0202".
# Note that a sequence like "0000" -> "0001" -> "0002" -> "0102" -> "0202"
# would be invalid,
# because the wheels of the lock become stuck after the display becomes the
# dead end "0102".
#
# Example 2:
#
# Input: deadends = ["8888"], target = "0009"
# Output: 1
# Explanation: We can turn the last wheel in reverse to move from "0000" ->
# "0009".
#
# Example 3:
#
# Input: deadends = ["8887","8889","8878","8898","8788","8988","7888","9888"],
# target = "8888"
# Output: -1
# Explanation: We cannot reach the target without getting stuck.
#
# Constraints:
#
# 1 <= deadends.length <= 500
#
# deadends[i].length == 4
#
# target.length == 4
#
# target will not be in the list deadends.
#
# target and deadends[i] consist of digits only.
#


# @lc code=start
from collections import deque
from typing import List, Set


class Solution:
    def openLock(self, deadends: List[str], target: str) -> int:
        """
        Interview explanation:
        Each lock state is a 4-digit node; turning one wheel ±1 is an edge.
        BFS from "0000" finds the shortest sequence avoiding deadends.

        Algorithm:
        - dead = set(deadends); if start in dead: -1
        - BFS queue (state, steps); for each digit try +1/-1; skip seen/dead

        Complexity: O(10^4) = O(1) states; O(1) space for the graph size.
        """
        dead: Set[str] = set(deadends)
        start = "0000"
        if start in dead:
            return -1
        if start == target:
            return 0
        q = deque([(start, 0)])
        seen = {start}
        while q:
            state, dist = q.popleft()
            for i in range(4):
                d = int(state[i])
                for nd in ((d + 1) % 10, (d - 1) % 10):
                    nxt = state[:i] + str(nd) + state[i + 1 :]
                    if nxt in seen or nxt in dead:
                        continue
                    if nxt == target:
                        return dist + 1
                    seen.add(nxt)
                    q.append((nxt, dist + 1))
        return -1

    def openLock_bidirectional(self, deadends: List[str], target: str) -> int:
        """
        Interview explanation:
        Alternate classic: bidirectional BFS from start and target, meeting in
        the middle — often faster in practice on large unweighted graphs.

        Algorithm:
        - Frontier sets begin/end; expand the smaller side each step
        - If neighbor in the other frontier: return steps

        Complexity: O(10^4) time/space worst case.
        """
        dead = set(deadends)
        start = "0000"
        if start in dead or target in dead:
            return -1
        if start == target:
            return 0
        front, back = {start}, {target}
        seen = set(dead)
        steps = 0

        def neighbors(state: str):
            for i in range(4):
                d = int(state[i])
                for nd in ((d + 1) % 10, (d - 1) % 10):
                    yield state[:i] + str(nd) + state[i + 1 :]

        while front and back:
            if len(front) > len(back):
                front, back = back, front
            steps += 1
            nxt_front = set()
            for state in front:
                for nei in neighbors(state):
                    if nei in back:
                        return steps
                    if nei not in seen:
                        seen.add(nei)
                        nxt_front.add(nei)
            front = nxt_front
        return -1
# @lc code=end

