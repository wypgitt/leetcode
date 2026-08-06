#
# @lc app=leetcode id=818 lang=python3
#
# [818] Race Car
#
# https://leetcode.com/problems/race-car/description/
#
# algorithms
# Hard (44.98%)
# Likes:    2032
# Dislikes: 192
# Total Accepted:    109K
# Total Submissions: 243K
# Testcase Example:  "3"
#
# Your car starts at position 0 and speed +1 on an infinite number line. Your
# car can go into negative positions. Your car drives automatically according
# to a sequence of instructions 'A' (accelerate) and 'R' (reverse):
#
# When you get an instruction 'A', your car does the following:
#
# position += speed
#
# speed *= 2
#
# When you get an instruction 'R', your car does the following:
#
# If your speed is positive then speed = -1
#
# otherwise speed = 1
#
# Your position stays the same.
#
# For example, after commands "AAR", your car goes to positions 0 --> 1 --> 3
# --> 3, and your speed goes to 1 --> 2 --> 4 --> -1.
#
# Given a target position target, return the length of the shortest sequence of
# instructions to get there.
#
# Example 1:
#
# Input: target = 3
# Output: 2
# Explanation:
# The shortest instruction sequence is "AA".
# Your position goes from 0 --> 1 --> 3.
#
# Example 2:
#
# Input: target = 6
# Output: 5
# Explanation:
# The shortest instruction sequence is "AAARA".
# Your position goes from 0 --> 1 --> 3 --> 7 --> 7 --> 6.
#
# Constraints:
#
# 1 <= target <= 10^4
#

# @lc code=start

from collections import deque
from functools import lru_cache


class Solution:
    def racecar(self, target: int) -> int:
        """
        Interview explanation:
        Position/speed start 0/1. A: pos+=speed, speed*=2; R: speed=-1 if >0 else 1.
        Shortest instruction sequence → BFS on (position, speed) with pruning.

        Algorithm (BFS):
        - Queue (pos, speed, steps); try A and R; bound |pos| < 2*target.

        Complexity: states roughly O(target log target); O(states) time/space.
        """
        q = deque([(0, 1)])
        seen = {(0, 1)}
        steps = 0
        while q:
            for _ in range(len(q)):
                pos, speed = q.popleft()
                if pos == target:
                    return steps
                # A
                np, ns = pos + speed, speed * 2
                if (np, ns) not in seen and abs(np) < target * 2:
                    seen.add((np, ns))
                    q.append((np, ns))
                # R
                ns2 = -1 if speed > 0 else 1
                if (pos, ns2) not in seen:
                    seen.add((pos, ns2))
                    q.append((pos, ns2))
            steps += 1
        return -1

    def racecar_dp(self, target: int) -> int:
        """
        Interview explanation:
        DP/memo on target distance: drive 2^k-1 steps toward target, then either
        reverse after overshoot or reverse earlier mid-way (classic race car DP).

        Algorithm:
        - dp(t): k = bit_length; exact 2^k-1 → k; else min of overshoot+R+dp
          and (k-1) A, R, m A, R, dp(rest).

        Complexity: O(target log^2 target) with memoization.
        """
        @lru_cache(None)
        def dp(t: int) -> int:
            k = t.bit_length()
            if (1 << k) - 1 == t:
                return k
            ans = k + 1 + dp((1 << k) - 1 - t)
            for m in range(k - 1):
                ans = min(
                    ans,
                    (k - 1) + 1 + m + 1 + dp(t - ((1 << (k - 1)) - 1) + ((1 << m) - 1)),
                )
            return ans

        return dp(target)
# @lc code=end
