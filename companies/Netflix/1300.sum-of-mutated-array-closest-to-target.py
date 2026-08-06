#
# @lc app=leetcode id=1300 lang=python3
#
# [1300] Sum of Mutated Array Closest to Target
#
# https://leetcode.com/problems/sum-of-mutated-array-closest-to-target/description/
#
# algorithms
# Medium (46.55%)
# Likes:    1221
# Dislikes: 156
# Total Accepted:    51.2K
# Total Submissions: 110K
# Testcase Example:  "[4,9,3]"
#
# Given an integer array arr and a target value target, return the integer
# value such that when we change all the integers larger than value in the
# given array to be equal to value, the sum of the array gets as close as
# possible (in absolute difference) to target.
#
# In case of a tie, return the minimum such integer.
#
# Notice that the answer is not neccesarilly a number from arr.
#
# Example 1:
#
# Input: arr = [4,9,3], target = 10
# Output: 3
# Explanation: When using 3 arr converts to [3, 3, 3] which sums 9 and that's
# the optimal answer.
#
# Example 2:
#
# Input: arr = [2,3,5], target = 10
# Output: 5
#
# Example 3:
#
# Input: arr = [60864,25176,27249,21296,20204], target = 56803
# Output: 11361
#
# Constraints:
#
# 1 <= arr.length <= 10^4
#
# 1 <= arr[i], target <= 10^5
#

# @lc code=start

from typing import List
import bisect


class Solution:
    def findBestValue(self, arr: List[int], target: int) -> int:
        """
        Interview explanation:
        Replace every arr[i]>value with value; minimize |sum-target|; break
        ties with smaller value. Sorted arr + binary search on value; for a
        candidate, sum = prefix of small + value * count of large.

        Algorithm:
        - Sort arr; prefix sums.
        - Binary search value in 0..max(arr) for sum closest to target;
          check mid and mid+1 style or scan best.

        Complexity: O(n log n + maxA log maxA) or O(n log n + n log maxA).
        """
        arr.sort()
        n = len(arr)
        prefix = [0]
        for x in arr:
            prefix.append(prefix[-1] + x)

        def mutated_sum(val: int) -> int:
            i = bisect.bisect_right(arr, val)
            return prefix[i] + val * (n - i)

        lo, hi = 0, arr[-1]
        while lo < hi:
            mid = (lo + hi) // 2
            if mutated_sum(mid) < target:
                lo = mid + 1
            else:
                hi = mid
        # lo is first value with sum >= target; compare lo-1 and lo
        candidates = {lo}
        if lo > 0:
            candidates.add(lo - 1)
        best_v = lo
        best_diff = abs(mutated_sum(lo) - target)
        for v in candidates:
            d = abs(mutated_sum(v) - target)
            if d < best_diff or (d == best_diff and v < best_v):
                best_diff = d
                best_v = v
        return best_v
# @lc code=end
