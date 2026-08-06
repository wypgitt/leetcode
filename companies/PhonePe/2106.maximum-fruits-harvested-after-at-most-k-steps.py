#
# @lc app=leetcode id=2106 lang=python3
#
# [2106] Maximum Fruits Harvested After at Most K Steps
#
# https://leetcode.com/problems/maximum-fruits-harvested-after-at-most-k-steps/description/
#
# algorithms
# Hard (60.97%)
# Likes:    1009
# Dislikes: 43
# Total Accepted:    87.6K
# Total Submissions: 143.7K
# Testcase Example:  "[[2,8],[6,3],[8,6]]\n5\n4"
#
# Fruits are available at some positions on an infinite x-axis. You are given a
# 2D integer array fruits where fruits[i] = [position_i, amount_i] depicts
# amount_i fruits at the position position_i. fruits is already sorted by
# position_i in ascending order, and each position_i is unique.
#
# You are also given an integer startPos and an integer k. Initially, you are at
# the position startPos. From any position, you can either walk to the left or
# right. It takes one step to move one unit on the x-axis, and you can walk at
# most k steps in total. For every position you reach, you harvest all the
# fruits at that position, and the fruits will disappear from that position.
#
# Return the maximum total number of fruits you can harvest.
#
#
#
# Example 1:
#
# Input: fruits = [[2,8],[6,3],[8,6]], startPos = 5, k = 4
# Output: 9
# Explanation:
# The optimal way is to:
# - Move right to position 6 and harvest 3 fruits
# - Move right to position 8 and harvest 6 fruits
# You moved 3 steps and harvested 3 + 6 = 9 fruits in total.
#
# Example 2:
#
# Input: fruits = [[0,9],[4,1],[5,7],[6,2],[7,4],[10,9]], startPos = 5, k = 4
# Output: 14
# Explanation:
# You can move at most k = 4 steps, so you cannot reach position 0 nor 10.
# The optimal way is to:
# - Harvest the 7 fruits at the starting position 5
# - Move left to position 4 and harvest 1 fruit
# - Move right to position 6 and harvest 2 fruits
# - Move right to position 7 and harvest 4 fruits
# You moved 1 + 3 = 4 steps and harvested 7 + 1 + 2 + 4 = 14 fruits in total.
#
# Example 3:
#
# Input: fruits = [[0,3],[6,4],[8,5]], startPos = 3, k = 2
# Output: 0
# Explanation:
# You can move at most k = 2 steps and cannot reach any position with fruits.
#
#
#
# Constraints:
#
#
# 1 <= fruits.length <= 10^5
#
#
# fruits[i].length == 2
#
#
# 0 <= startPos, position_i <= 2 * 10^5
#
#
# position_i-1 < position_i for any i > 0 (0-indexed)
#
#
# 1 <= amount_i <= 10^4
#
#
# 0 <= k <= 2 * 10^5
#


# @lc code=start
from typing import List
import bisect


class Solution:
    def maxTotalFruits(self, fruits: List[List[int]], startPos: int, k: int) -> int:
        """
        Interview explanation:
        Fruits at positions (sorted). Collect max fruits with at most k steps
        starting at startPos (can go left then right or right then left).

        Algorithm:
        - Prefix sums of amounts.
        - Window [L,R] is collectible if min steps to cover [posL,posR] from
          startPos <= k: min( abs(start-posL)+ (posR-posL), abs(start-posR)+(posR-posL) ).
        - Expand R, shrink L while infeasible; track max prefix[R+1]-prefix[L].

        Complexity: O(n) time, O(n) space.
        """
        n = len(fruits)
        pos = [p for p, _ in fruits]
        pref = [0] * (n + 1)
        for i, (_, a) in enumerate(fruits):
            pref[i + 1] = pref[i] + a

        def steps(L: int, R: int) -> int:
            left, right = pos[L], pos[R]
            return min(
                abs(startPos - left) + (right - left),
                abs(startPos - right) + (right - left),
            )

        ans = 0
        L = 0
        for R in range(n):
            while L <= R and steps(L, R) > k:
                L += 1
            if L <= R:
                ans = max(ans, pref[R + 1] - pref[L])
        return ans

    def maxTotalFruits_binary_search(self, fruits: List[List[int]], startPos: int, k: int) -> int:
        """
        Interview explanation:
        Alternate: for each rightmost position, binary-search farthest left
        still reachable within k (or vice versa).

        Algorithm:
        - Prefix sums; for each R, compute needed left bound from go-right-first
          / go-left-first formulas; bisect.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(fruits)
        pos = [p for p, _ in fruits]
        pref = [0] * (n + 1)
        for i, (_, a) in enumerate(fruits):
            pref[i + 1] = pref[i] + a
        ans = 0
        for R in range(n):
            # go to right first then left: steps = (pos[R]-start) + (pos[R]-pos[L]) if start<=pos[R]
            # cover interval [pos[L], pos[R]]
            lo, hi = 0, R
            best = R + 1
            while lo <= hi:
                mid = (lo + hi) // 2
                left, right = pos[mid], pos[R]
                need = min(abs(startPos - left) + right - left, abs(startPos - right) + right - left)
                if need <= k:
                    best = mid
                    hi = mid - 1
                else:
                    lo = mid + 1
            if best <= R:
                ans = max(ans, pref[R + 1] - pref[best])
        return ans
# @lc code=end

