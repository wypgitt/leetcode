#
# @lc app=leetcode id=3957 lang=python3
#
# [3957] Maximum Sum of M Non-Overlapping Subarrays II
#
# https://leetcode.com/problems/maximum-sum-of-m-non-overlapping-subarrays-ii/description/
#
# algorithms
# Hard (16.67%)
# Likes:    14
# Dislikes: 6
# Total Accepted:    2.2K
# Total Submissions: 13.3K
# Testcase Example:  "[4,1,-5,2]\n2\n1\n3"
#
#
# You are given an integer array nums of length n, and three integers m,
# l, and r.
#
# Your task is to select at least one and at most m non-overlapping
# subarrays from nums such that:
#
# Each selected subarray has a length between [l, r] (inclusive).
#
# The total sum of all selected subarrays is maximized.
#
# Return the maximum total sum you can achieve.
#
# Example 1:
#
# Input: nums = [4,1,-5,2], m = 2, l = 1, r = 3
#
# Output: 7
#
# Explanation:
#
# One optimal strategy is to:
#
# Select the subarray [4, 1] with sum 4 + 1 = 5 and the subarray [2] with
# sum 2. Both subarrays have length between [l, r].
#
# The total sum of these subarrays is 5 + 2 = 7, which is the maximum
# achievable sum with at most m = 2 subarrays.
#
# Example 2:
#
# Input: nums = [1,0,3,4], m = 2, l = 1, r = 2
#
# Output: 8
#
# Explanation:
#
# One optimal strategy is to:
#
# Select the subarray [1] with sum 1 and the subarray [3, 4] with sum 3 +
# 4 = 7. Both subarrays have length between [l, r].
#
# The total sum of these subarrays is 1 + 7 = 8, which is the maximum
# achievable sum with at most m = 2 subarrays.
#
# Example 3:
#
# Input: nums = [-1,7,-4], m = 1, l = 2, r = 3
#
# Output: 6
#
# Explanation:
#
# Select the subarray [-1, 7] from nums which has length between [l, r].
#
# The total sum of this subarray is -1 + 7 = 6, which is the maximum
# achievable sum with at most m = 1 subarray.
#
# Example 4:
#
# Input: nums = [-3,-4,-1], m = 2, l = 1, r = 2
#
# Output: -1
#
# Explanation:
#
# All subarrays of nums have negative sums. The optimal strategy is to
# select the subarray [-1], which has length between [l, r].
#
# The total sum of this subarray is -1, which is the maximum achievable
# sum with at most m = 2 subarrays.
#
# Constraints:
#
# 1 <= n == nums.length <= 10^5
#
# -10^5 <= nums[i] <= 10^5​​​​​​​
#
# 1 <= m <= n
#
# 1 <= l <= r <= n
#

# @lc code=start
from collections import deque


class Solution:
    def maximumSum(self, nums: list[int], m: int, l: int, r: int) -> int:
        """
        Interview explanation:
        Same as the I-version but n≤1e5, so O(n·m) is too slow. The optimum
        vs segment-count is concave → WQS (Aliens) binary search on a per-
        segment penalty, with O(n) monoqueue DP per check.

        Algorithm:
        - fentoluric stores the input.
        - dpWithoutLimit(penalty): max sum with unlimited segments, each
          costing `penalty`; also track segment count (prefer fewer on ties).
        - If unlimited optimum already uses ≤m segments, return it.
        - Else binary-search penalty so the optimum uses ≤m segments; recover
          score as dp + m·penalty (exact-m convex dual).

        Complexity: O(n log Σ) time, O(n) space.
        """
        fentoluric = nums
        n = len(fentoluric)
        s = [0] * (n + 1)
        pos_sum = 0
        for i, x in enumerate(fentoluric):
            s[i + 1] = s[i] + x
            if x > 0:
                pos_sum += x

        def less(a, b):
            return a[0] < b[0] or (a[0] == b[0] and a[1] > b[1])

        def dp_without_limit(penalty: int):
            f = [(0, 0)] * (n + 1)
            q = deque()
            res = (-10**30, 0)
            for i in range(l):
                f[i] = (0, 0)
            for i in range(l, n + 1):
                j = i - l
                v = (f[j][0] - s[j], f[j][1])
                while q and less((f[q[-1]][0] - s[q[-1]], f[q[-1]][1]), v):
                    q.pop()
                q.append(j)
                j = q[0]
                choose = (f[j][0] - s[j] + s[i] - penalty, f[j][1] + 1)
                if less(res, choose):
                    res = choose
                f[i] = choose if less(f[i - 1], choose) else f[i - 1]
                if q[0] <= i - r:
                    q.popleft()
            return res

        res0 = dp_without_limit(0)
        if res0[1] <= m:
            return res0[0]

        ans = 0
        left, right = 0, pos_sum + 1
        while left + 1 < right:
            mid = (left + right) // 2
            res = dp_without_limit(mid)
            if res[1] <= m:
                ans = res[0] + m * mid
                right = mid
            else:
                left = mid
        return ans
# @lc code=end
