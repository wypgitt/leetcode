#
# @lc app=leetcode id=1552 lang=python3
#
# [1552] Magnetic Force Between Two Balls
#
# https://leetcode.com/problems/magnetic-force-between-two-balls/description/
#
# algorithms
# Medium (72.49%)
# Likes:    3277
# Dislikes: 276
# Total Accepted:    242K
# Total Submissions: 334K
# Testcase Example:  "[1,2,3,4,7]"
#
# In the universe Earth C-137, Rick discovered a special form of magnetic force
# between two balls if they are put in his new invented basket. Rick has n
# empty baskets, the i^th basket is at position[i], Morty has m balls and needs
# to distribute the balls into the baskets such that the minimum magnetic force
# between any two balls is maximum.
#
# Rick stated that magnetic force between two different balls at positions x
# and y is |x - y|.
#
# Given the integer array position and the integer m. Return the required
# force.
#
# Example 1:
#
# Input: position = [1,2,3,4,7], m = 3
# Output: 3
# Explanation: Distributing the 3 balls into baskets 1, 4 and 7 will make the
# magnetic force between ball pairs [3, 3, 6]. The minimum magnetic force is 3.
# We cannot achieve a larger minimum magnetic force than 3.
#
# Example 2:
#
# Input: position = [5,4,3,2,1,1000000000], m = 2
# Output: 999999999
# Explanation: We can use baskets 1 and 1000000000.
#
# Constraints:
#
# n == position.length
#
# 2 <= n <= 10^5
#
# 1 <= position[i] <= 10^9
#
# All integers in position are distinct.
#
# 2 <= m <= position.length
#

# @lc code=start
from typing import List


class Solution:
    def maxDistance(self, position: List[int], m: int) -> int:
        """
        Interview explanation:
        Maximize minimum magnetic force (= distance) between m balls in sorted
        positions. Binary search the answer: for mid force, greedily place balls
        with gaps >= mid; feasible → try larger.

        Algorithm (binary search + greedy):
        - Sort position; lo=1, hi=max-min.
        - can(d): place first at pos[0], next only if gap>=d; need m placed.
        - Binary search largest d with can(d).

        Complexity: O(n log n + n log D) time, O(1)/O(n) space for sort.
        """
        position.sort()
        lo, hi = 1, position[-1] - position[0]
        ans = 0

        def can(d: int) -> bool:
            placed, last = 1, position[0]
            for x in position[1:]:
                if x - last >= d:
                    placed += 1
                    last = x
                    if placed >= m:
                        return True
            return False

        while lo <= hi:
            mid = (lo + hi) // 2
            if can(mid):
                ans = mid
                lo = mid + 1
            else:
                hi = mid - 1
        return ans
# @lc code=end

