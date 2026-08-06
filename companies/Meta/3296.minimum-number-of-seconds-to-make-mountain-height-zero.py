#
# @lc app=leetcode id=3296 lang=python3
#
# [3296] Minimum Number of Seconds to Make Mountain Height Zero
#
# https://leetcode.com/problems/minimum-number-of-seconds-to-make-mountain-height-zero/description/
#
# algorithms
# Medium (58.26%)
# Likes:    618
# Dislikes: 95
# Total Accepted:    106.6K
# Total Submissions: 182.9K
# Testcase Example:  "4\n[2,1,1]"
#
#
# You are given an integer mountainHeight denoting the height of a
# mountain.
#
# You are also given an integer array workerTimes representing the work
# time of workers in seconds.
#
# Each worker may reduce the mountain's height by any non-negative integer
# amount. If worker i reduces the height by x, then:
#
# reducing the first unit of height takes workerTimes[i] seconds,
#
# reducing the second unit takes workerTimes[i] * 2 seconds,
#
# ...
#
# reducing the x-th unit takes workerTimes[i] * x seconds.
#
# The total time spent by worker i is the sum of the times required for
# all x units they reduce. As all workers operate simultaneously, the
# total time required is the maximum time spent by any worker.
#
# Return an integer representing the minimum number of seconds required
# for the workers to make the height of the mountain 0.
#
# Example 1:
#
# Input: mountainHeight = 4, workerTimes = [2,1,1]
#
# Output: 3
#
# Explanation:
#
# One way the height of the mountain can be reduced to 0 is:
#
# Worker 0 reduces the height by 1, taking workerTimes[0] = 2 seconds.
#
# Worker 1 reduces the height by 2, taking workerTimes[1] + workerTimes[1]
# * 2 = 3 seconds.
#
# Worker 2 reduces the height by 1, taking workerTimes[2] = 1 second.
#
# Since they work simultaneously, the minimum time needed is max(2, 3, 1)
# = 3 seconds.
#
# Example 2:
#
# Input: mountainHeight = 10, workerTimes = [3,2,2,4]
#
# Output: 12
#
# Explanation:
#
# Worker 0 reduces the height by 2, taking workerTimes[0] + workerTimes[0]
# * 2 = 9 seconds.
#
# Worker 1 reduces the height by 3, taking workerTimes[1] + workerTimes[1]
# * 2 + workerTimes[1] * 3 = 12 seconds.
#
# Worker 2 reduces the height by 3, taking workerTimes[2] + workerTimes[2]
# * 2 + workerTimes[2] * 3 = 12 seconds.
#
# Worker 3 reduces the height by 2, taking workerTimes[3] + workerTimes[3]
# * 2 = 12 seconds.
#
# The number of seconds needed is max(9, 12, 12, 12) = 12 seconds.
#
# Example 3:
#
# Input: mountainHeight = 5, workerTimes = [1]
#
# Output: 15
#
# Explanation:
#
# There is only one worker in this example, so the answer is
# workerTimes[0] + workerTimes[0] * 2 + workerTimes[0] * 3 +
# workerTimes[0] * 4 + workerTimes[0] * 5 = 15.
#
# Constraints:
#
# 1 <= mountainHeight <= 10^5
#
# 1 <= workerTimes.length <= 10^4
#
# 1 <= workerTimes[i] <= 10^6
#

# @lc code=start
from typing import List


class Solution:
    def minNumberOfSeconds(self, mountainHeight: int, workerTimes: List[int]) -> int:
        """
        Interview explanation:
        Workers dig in parallel; worker w removing x units costs w*x*(x+1)/2.
        Minimize the makespan T.

        Algorithm:
        - Binary search T.
        - For fixed T, each worker contributes max x with w*x*(x+1)/2 <= T.
        - Feasible if total units >= mountainHeight.
        - Alternate: solve x via integer sqrt instead of inner binary search.

        Complexity: O(m log H * log T) time, O(1) space.
        """
        def units_for(w: int, T: int) -> int:
            lo, hi = 0, mountainHeight
            while lo < hi:
                mid = (lo + hi + 1) // 2
                if w * mid * (mid + 1) // 2 <= T:
                    lo = mid
                else:
                    hi = mid - 1
            return lo

        lo, hi = 0, max(workerTimes) * mountainHeight * (mountainHeight + 1) // 2
        while lo < hi:
            mid = (lo + hi) // 2
            if sum(units_for(w, mid) for w in workerTimes) >= mountainHeight:
                hi = mid
            else:
                lo = mid + 1
        return lo

    def minNumberOfSeconds_sqrt(self, mountainHeight: int, workerTimes: List[int]) -> int:
        """
        Interview explanation:
        Same binary search on T; closed-form x ≈ (-1 + sqrt(1+8T/w))/2.

        Algorithm:
        - units = floor((-1 + isqrt(1 + 8T//w)) / 2), capped by height.

        Complexity: O(m log T) time, O(1) space.
        """
        from math import isqrt

        def units_for(w: int, T: int) -> int:
            # w*x*(x+1)/2 <= T → x(x+1) <= 2T/w
            x = (isqrt(1 + 8 * (T // w)) - 1) // 2
            return min(x, mountainHeight)

        lo, hi = 0, max(workerTimes) * mountainHeight * (mountainHeight + 1) // 2
        while lo < hi:
            mid = (lo + hi) // 2
            if sum(units_for(w, mid) for w in workerTimes) >= mountainHeight:
                hi = mid
            else:
                lo = mid + 1
        return lo
# @lc code=end
