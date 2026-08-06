#
# @lc app=leetcode id=2604 lang=python3
#
# [2604] Minimum Time to Eat All Grains
#
# https://leetcode.com/problems/minimum-time-to-eat-all-grains/description/
#
# algorithms
# Hard (41.08%)
# Likes:    50
# Dislikes: 4
# Total Accepted:    2.3K
# Total Submissions: 5.7K
# Testcase Example:  "[3,6,7]\n[2,4,7,9]"
#
#
# There are n hens and m grains on a line. You are given the initial
# positions of the hens and the grains in two integer arrays hens and
# grains of size n and m respectively.
#
# Any hen can eat a grain if they are on the same position. The time taken
# for this is negligible. One hen can also eat multiple grains.
#
# In 1 second, a hen can move right or left by 1 unit. The hens can move
# simultaneously and independently of each other.
#
# Return the minimum time to eat all grains if the hens act optimally.
#
# Example 1:
#
# Input: hens = [3,6,7], grains = [2,4,7,9]
# Output: 2
# Explanation:
# One of the ways hens eat all grains in 2 seconds is described below:
# - The first hen eats the grain at position 2 in 1 second.
# - The second hen eats the grain at position 4 in 2 seconds.
# - The third hen eats the grains at positions 7 and 9 in 2 seconds.
# So, the maximum time needed is 2.
# It can be proven that the hens cannot eat all grains before 2 seconds.
#
# Example 2:
#
# Input: hens = [4,6,109,111,213,215], grains = [5,110,214]
# Output: 1
# Explanation:
# One of the ways hens eat all grains in 1 second is described below:
# - The first hen eats the grain at position 5 in 1 second.
# - The fourth hen eats the grain at position 110 in 1 second.
# - The sixth hen eats the grain at position 214 in 1 second.
# - The other hens do not move.
# So, the maximum time needed is 1.
#
# Constraints:
#
# 1 <= hens.length, grains.length <= 2*10^4
#
# 0 <= hens[i], grains[j] <= 10^9
#
# @lc code=start
from typing import List


class Solution:
    def minimumTime(self, hens: List[int], grains: List[int]) -> int:
        """
        Interview explanation:
        Hens and grains lie on a number line; hens move at speed 1 and eat
        instantly on contact. Hens work in parallel. Find the minimum time T
        so every grain can be eaten by some hen.

        Algorithm:
        - Sort hens and grains; binary search on time T.
        - Greedy check: assign remaining leftmost grains left-to-right to hens.
          For hen h covering a contiguous prefix starting at grains[j]:
          - If grains[j] >= h: only go right, reach h + T.
          - Else if h - grains[j] > T: this hen (and all to its right) cannot
            reach the leftmost grain -> fail.
          - Else leftmost L = grains[j], left = h - L; farthest reach is
            max(L + (T - left), h + (T - left) // 2)
            (left-then-right vs right-then-left).

        Complexity: O((n + m) log n + (n + m) log A) time, O(1) extra space
        after sorting (A = search range on time).
        """
        if not grains:
            return 0
        hens.sort()
        grains.sort()
        m = len(grains)

        def can(t: int) -> bool:
            j = 0
            for h in hens:
                if j >= m:
                    return True
                if grains[j] > h + t:
                    # Grain is to the right beyond this hen; try a later hen.
                    continue
                if grains[j] >= h:
                    while j < m and grains[j] <= h + t:
                        j += 1
                else:
                    if h - grains[j] > t:
                        return False
                    left = h - grains[j]
                    # left-then-right: L + (t - left)
                    # right-then-left: h + (t - left) // 2
                    limit = max(grains[j] + (t - left), h + (t - left) // 2)
                    while j < m and grains[j] <= limit:
                        j += 1
            return j >= m

        lo = 0
        hi = max(hens[-1], grains[-1]) - min(hens[0], grains[0]) + (
            grains[-1] - grains[0]
        )
        while lo < hi:
            mid = (lo + hi) // 2
            if can(mid):
                hi = mid
            else:
                lo = mid + 1
        return lo
# @lc code=end
