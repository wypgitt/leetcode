#
# @lc app=leetcode id=3489 lang=python3
#
# [3489] Zero Array Transformation IV
#
# https://leetcode.com/problems/zero-array-transformation-iv/description/
#
# algorithms
# Medium (31.63%)
# Likes:    148
# Dislikes: 24
# Total Accepted:    12.3K
# Total Submissions: 39K
# Testcase Example:  "[2,0,2]\n[[0,2,1],[0,2,1],[1,1,3]]"
#
#
# You are given an integer array nums of length n and a 2D array queries,
# where queries[i] = [l_i, r_i, val_i].
#
# Each queries[i] represents the following action on nums:
#
# Select a subset of indices in the range [l_i, r_i] from nums.
#
# Decrement the value at each selected index by exactly val_i.
#
# A Zero Array is an array with all its elements equal to 0.
#
# Return the minimum possible non-negative value of k, such that after
# processing the first k queries in sequence, nums becomes a Zero Array.
# If no such k exists, return -1.
#
# Example 1:
#
# Input: nums = [2,0,2], queries = [[0,2,1],[0,2,1],[1,1,3]]
#
# Output: 2
#
# Explanation:
#
# For query 0 (l = 0, r = 2, val = 1):
#
# Decrement the values at indices [0, 2] by 1.
#
# The array will become [1, 0, 1].
#
# For query 1 (l = 0, r = 2, val = 1):
#
# Decrement the values at indices [0, 2] by 1.
#
# The array will become [0, 0, 0], which is a Zero Array. Therefore, the
# minimum value of k is 2.
#
# Example 2:
#
# Input: nums = [4,3,2,1], queries = [[1,3,2],[0,2,1]]
#
# Output: -1
#
# Explanation:
#
# It is impossible to make nums a Zero Array even after all the queries.
#
# Example 3:
#
# Input: nums = [1,2,3,2,1], queries =
# [[0,1,1],[1,2,1],[2,3,2],[3,4,1],[4,4,1]]
#
# Output: 4
#
# Explanation:
#
# For query 0 (l = 0, r = 1, val = 1):
#
# Decrement the values at indices [0, 1] by 1.
#
# The array will become [0, 1, 3, 2, 1].
#
# For query 1 (l = 1, r = 2, val = 1):
#
# Decrement the values at indices [1, 2] by 1.
#
# The array will become [0, 0, 2, 2, 1].
#
# For query 2 (l = 2, r = 3, val = 2):
#
# Decrement the values at indices [2, 3] by 2.
#
# The array will become [0, 0, 0, 0, 1].
#
# For query 3 (l = 3, r = 4, val = 1):
#
# Decrement the value at index 4 by 1.
#
# The array will become [0, 0, 0, 0, 0]. Therefore, the minimum value of k
# is 4.
#
# Example 4:
#
# Input: nums = [1,2,3,2,6], queries =
# [[0,1,1],[0,2,1],[1,4,2],[4,4,4],[3,4,1],[4,4,5]]
#
# Output: 4
#
# Constraints:
#
# 1 <= nums.length <= 10
#
# 0 <= nums[i] <= 1000
#
# 1 <= queries.length <= 1000
#
# queries[i] = [l_i, r_i, val_i]
#
# 0 <= l_i <= r_i < nums.length
#
# 1 <= val_i <= 10
#

# @lc code=start
from typing import List


class Solution:
    def minZeroArray(self, nums: List[int], queries: List[List[int]]) -> int:
        """
        Interview explanation:
        Each query may subtract val from any subset of [l,r]. Index i becomes
        zero iff nums[i] is a subset-sum of the vals from queries covering i.
        Find minimal prefix of queries that works for all indices (n ≤ 10).

        Algorithm:
        - Per index, maintain a boolean knapsack of reachable sums up to nums[i].
        - Apply queries online; return first k where every index can form nums[i].

        Complexity: O(q * n * max(nums)) time, O(n * max(nums)) space.
        """
        if all(x == 0 for x in nums):
            return 0

        n = len(nums)
        # reach[i][s] = whether sum s is reachable for index i
        reach = [[False] * (nums[i] + 1) for i in range(n)]
        for i in range(n):
            reach[i][0] = True

        for k, (l, r, val) in enumerate(queries):
            for i in range(l, r + 1):
                target = nums[i]
                if target == 0:
                    continue
                dp = reach[i]
                for s in range(target, val - 1, -1):
                    if dp[s - val]:
                        dp[s] = True
            if all(reach[i][nums[i]] for i in range(n)):
                return k + 1
        return -1

    def minZeroArray_binary_search(self, nums: List[int], queries: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: binary search the smallest k, checking knapsack feasibility
        with the first k queries.

        Algorithm:
        - lo/hi on k; for each mid rebuild reachable sets per index.

        Complexity: O(log q * q * n * max(nums)) time, O(n * max(nums)) space.
        """
        if all(x == 0 for x in nums):
            return 0

        n = len(nums)

        def ok(k: int) -> bool:
            for i, target in enumerate(nums):
                if target == 0:
                    continue
                dp = [False] * (target + 1)
                dp[0] = True
                for j in range(k):
                    l, r, val = queries[j]
                    if not (l <= i <= r):
                        continue
                    for s in range(target, val - 1, -1):
                        if dp[s - val]:
                            dp[s] = True
                if not dp[target]:
                    return False
            return True

        lo, hi, ans = 1, len(queries), -1
        while lo <= hi:
            mid = (lo + hi) // 2
            if ok(mid):
                ans = mid
                hi = mid - 1
            else:
                lo = mid + 1
        return ans
# @lc code=end
