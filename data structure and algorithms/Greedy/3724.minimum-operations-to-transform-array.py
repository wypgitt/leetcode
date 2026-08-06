#
# @lc app=leetcode id=3724 lang=python3
#
# [3724] Minimum Operations to Transform Array
#
# https://leetcode.com/problems/minimum-operations-to-transform-array/description/
#
# algorithms
# Medium (40.34%)
# Likes:    90
# Dislikes: 7
# Total Accepted:    15K
# Total Submissions: 37.1K
# Testcase Example:  "[2,8]\n[1,7,3]"
#
#
# You are given two integer arrays nums1 of length n and nums2 of length n
# + 1.
#
# You want to transform nums1 into nums2 using the minimum number of
# operations.
#
# You may perform the following operations any number of times, each time
# choosing an index i:
#
# Increase nums1[i] by 1.
#
# Decrease nums1[i] by 1.
#
# Append nums1[i] to the end of the array.
#
# Return the minimum number of operations required to transform nums1 into
# nums2.
#
# Example 1:
#
# Input: nums1 = [2,8], nums2 = [1,7,3]
#
# Output: 4
#
# Explanation:
#
#                         Step
#                         i
#                         Operation
#                         nums1[i]
#                         Updated nums1
#
#                         1
#                         0
#                         Append
#                         -
#                         [2, 8, 2]
#
#                         2
#                         0
#                         Decrement
#                         Decreases to 1
#                         [1, 8, 2]
#
#                         3
#                         1
#                         Decrement
#                         Decreases to 7
#                         [1, 7, 2]
#
#                         4
#                         2
#                         Increment
#                         Increases to 3
#                         [1, 7, 3]
#
# Thus, after 4 operations nums1 is transformed into nums2.
#
# Example 2:
#
# Input: nums1 = [1,3,6], nums2 = [2,4,5,3]
#
# Output: 4
#
# Explanation:
#
#                         Step
#                         i
#                         Operation
#                         nums1[i]
#                         Updated nums1
#
#                         1
#                         1
#                         Append
#                         -
#                         [1, 3, 6, 3]
#
#                         2
#                         0
#                         Increment
#                         Increases to 2
#                         [2, 3, 6, 3]
#
#                         3
#                         1
#                         Increment
#                         Increases to 4
#                         [2, 4, 6, 3]
#
#                         4
#                         2
#                         Decrement
#                         Decreases to 5
#                         [2, 4, 5, 3]
#
# Thus, after 4 operations nums1 is transformed into nums2.
#
# Example 3:
#
# Input: nums1 = [2], nums2 = [3,4]
#
# Output: 3
#
# Explanation:
#
#                         Step
#                         i
#                         Operation
#                         nums1[i]
#                         Updated nums1
#
#                         1
#                         0
#                         Increment
#                         Increases to 3
#                         [3]
#
#                         2
#                         0
#                         Append
#                         -
#                         [3, 3]
#
#                         3
#                         1
#                         Increment
#                         Increases to 4
#                         [3, 4]
#
# Thus, after 3 operations nums1 is transformed into nums2.
#
# Constraints:
#
# 1 <= n == nums1.length <= 10^5
#
# nums2.length == n + 1
#
# 1 <= nums1[i], nums2[i] <= 10^5
#

# @lc code=start
from math import inf
from typing import List


class Solution:
    def minOperations(self, nums1: List[int], nums2: List[int]) -> int:
        """
        Interview explanation:
        Always pay |nums1[i] - nums2[i]| for the first n positions, plus 1 for
        the mandatory append. The appended value nums2[n] can "ride" an inc/dec
        path between nums1[i] and nums2[i] for free if it lies in that range;
        otherwise pay the closest endpoint distance once.

        Algorithm:
        - ans = 1 + sum |a - b| over zip(nums1, nums2[:n]).
        - If some pair's interval covers nums2[-1], done; else add min distance
          from nums2[-1] to any nums1[i] or nums2[i].

        Complexity: O(n) time, O(1) space.
        """
        ans = 1
        ok = False
        d = inf
        target = nums2[-1]
        for x, y in zip(nums1, nums2):
            hi, lo = (x, y) if x >= y else (y, x)
            ans += hi - lo
            d = min(d, abs(hi - target), abs(lo - target))
            ok = ok or lo <= target <= hi
        if not ok:
            ans += d
        return ans

    def minOperations_explicit(self, nums1: List[int], nums2: List[int]) -> int:
        """
        Interview explanation:
        Alternate: same greedy with explicit max/min calls.

        Algorithm:
        - Identical accounting; track whether target is covered by any segment.

        Complexity: O(n) time, O(1) space.
        """
        ans, extra, covered = 1, inf, False
        t = nums2[-1]
        for a, b in zip(nums1, nums2):
            ans += abs(a - b)
            extra = min(extra, abs(a - t), abs(b - t))
            if min(a, b) <= t <= max(a, b):
                covered = True
        return ans if covered else ans + extra
# @lc code=end

