#
# @lc app=leetcode id=3356 lang=python3
#
# [3356] Zero Array Transformation II
#
# https://leetcode.com/problems/zero-array-transformation-ii/description/
#
# algorithms
# Medium (43.53%)
# Likes:    1064
# Dislikes: 86
# Total Accepted:    136.4K
# Total Submissions: 313.4K
# Testcase Example:  "[2,0,2]\n[[0,2,1],[0,2,1],[1,1,3]]"
#
#
# You are given an integer array nums of length n and a 2D array queries
# where queries[i] = [l_i, r_i, val_i].
#
# Each queries[i] represents the following action on nums:
#
# Decrement the value at each index in the range [l_i, r_i] in nums by at
# most val_i.
#
# The amount by which each value is decremented can be chosen
# independently for each index.
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
# For i = 0 (l = 0, r = 2, val = 1):
#
# Decrement values at indices [0, 1, 2] by [1, 0, 1] respectively.
#
# The array will become [1, 0, 1].
#
# For i = 1 (l = 0, r = 2, val = 1):
#
# Decrement values at indices [0, 1, 2] by [1, 0, 1] respectively.
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
# For i = 0 (l = 1, r = 3, val = 2):
#
# Decrement values at indices [1, 2, 3] by [2, 2, 1] respectively.
#
# The array will become [4, 1, 0, 0].
#
# For i = 1 (l = 0, r = 2, val = 1):
#
# Decrement values at indices [0, 1, 2] by [1, 1, 0] respectively.
#
# The array will become [3, 0, 0, 0], which is not a Zero Array.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 0 <= nums[i] <= 5 * 10^5
#
# 1 <= queries.length <= 10^5
#
# queries[i].length == 3
#
# 0 <= l_i <= r_i < nums.length
#
# 1 <= val_i <= 5
#

# @lc code=start

from typing import List


class Solution:
    def minZeroArray(self, nums: List[int], queries: List[List[int]]) -> int:
        """
        Interview explanation:
        First k queries each allow decreasing every index in [l,r] by up to val.
        Find minimal k so total capacity ≥ nums[i] everywhere (−1 if impossible).

        Algorithm:
        - Binary search k; check with difference array of first k queries.
        - Edge: already zero → 0.

        Complexity: O((n+q) log q) time, O(n) space.
        """
        n = len(nums)
        if all(x == 0 for x in nums):
            return 0

        def ok(k: int) -> bool:
            diff = [0] * (n + 1)
            for i in range(k):
                l, r, val = queries[i]
                diff[l] += val
                diff[r + 1] -= val
            cur = 0
            for i in range(n):
                cur += diff[i]
                if cur < nums[i]:
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

    def minZeroArray_line_sweep(self, nums: List[int], queries: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate O(n+q): expand k while maintaining a difference array; when
        capacity at i is short, consume more queries covering i.

        Algorithm:
        - Two pointers / online: for i from 0..n-1, while sum < nums[i], apply
          next query into the diff structure.

        Complexity: O(n + q) time, O(n) space.
        """
        n = len(nums)
        diff = [0] * (n + 1)
        k = cur = 0
        for i in range(n):
            cur += diff[i]
            while cur < nums[i] and k < len(queries):
                l, r, val = queries[k]
                k += 1
                if r < i:
                    continue
                if l <= i:
                    cur += val
                else:
                    diff[l] += val
                diff[r + 1] -= val
            if cur < nums[i]:
                return -1
        return k
# @lc code=end
