#
# @lc app=leetcode id=3911 lang=python3
#
# [3911] K-th Smallest Remaining Even Integer in Subarray Queries
#
# https://leetcode.com/problems/k-th-smallest-remaining-even-integer-in-subarray-queries/description/
#
# algorithms
# Hard (29.81%)
# Likes:    38
# Dislikes: 3
# Total Accepted:    4.7K
# Total Submissions: 15.8K
# Testcase Example:  "[1,4,7]\n[[0,2,1],[1,1,2],[0,0,3]]"
#
#
# You are given an integer array nums where nums is strictly increasing.
#
# You are also given a 2D integer array queries, where queries[i] = [l_i,
# r_i, k_i].
#
# For each query [l_i, r_i, k_i]:
#
# Consider the subarray nums[l_i..r_i]
#
# From the infinite sequence of all positive even integers: 2, 4, 6, 8,
# 10, 12, 14, ...
#
# Remove all elements that appear in the subarray nums[l_i..r_i].
#
# Find the k_i^th smallest integer remaining in the sequence after the
# removals.
#
# Return an integer array ans, where ans[i] is the result for the i^th
# query.
#
# Example 1:
#
# Input: nums = [1,4,7], queries = [[0,2,1],[1,1,2],[0,0,3]]
#
# Output: [2,6,6]
#
# Explanation:
#
#                         i
#                         queries[i]
#                         nums[l_i..r_i]
#                         Removed
#
#                         Evens
#                         Remaining
#
#                         Evens
#                         k_i
#                         ans[i]
#
#                         0
#                         [0, 2, 1]
#                         [1, 4, 7]
#                         [4]
#                         2, 6, 8, ...
#                         1
#                         2
#
#                         1
#                         [1, 1, 2]
#                         [4]
#                         [4]
#                         2, 6, 8, ...
#                         2
#                         6
#
#                         2
#                         [0, 0, 3]
#                         [1]
#                         []
#                         2, 4, 6, ...
#                         3
#                         6
#
# Thus, ans = [2, 6, 6].
#
# Example 2:
#
# Input: nums = [2,5,8], queries = [[0,1,2],[1,2,1],[0,2,4]]
#
# Output: [6,2,12]
#
# Explanation:
#
#                         i
#                         queries[i]
#                         nums[l_i..r_i]
#                         Removed
#
#                         Evens
#                         Remaining
#
#                         Evens
#                         k_i
#                         ans[i]
#
#                         0
#                         [0, 1, 2]
#                         [2, 5]
#                         [2]
#                         4, 6, 8, ...
#                         2
#                         6
#
#                         1
#                         [1, 2, 1]
#                         [5, 8]
#                         [8]
#                         2, 4, 6, ...
#                         1
#                         2
#
#                         2
#                         [0, 2, 4]
#                         [2, 5, 8]
#                         [2, 8]
#                         4, 6, 10, 12, ...
#                         4
#                         12
#
# Thus, ans = [6, 2, 12].
#
# Example 3:
#
# Input: nums = [3,6], queries = [[0,1,1],[1,1,3]]
#
# Output: [2,8]
#
# Explanation:
#
#                         i
#                         queries[i]
#                         nums[l_i..r_i]
#                         Removed
#
#                         Evens
#                         Remaining
#
#                         Evens
#                         k_i
#                         ans[i]
#
#                         0
#                         [0, 1, 1]
#                         [3, 6]
#                         [6]
#                         2, 4, 8, ...
#                         1
#                         2
#
#                         1
#                         [1, 1, 3]
#                         [6]
#                         [6]
#                         2, 4, 8, ...
#                         3
#                         8
#
# Thus, ans = [2, 8].
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# nums is strictly increasing
#
# 1 <= queries.length <= 10^5
#
# queries[i] = [l_i, r_i, k_i]
#
# 0 <= l_i <= r_i < nums.length
#
# 1 <= k_i <= 10^9​​​​​​​
#

# @lc code=start
import bisect


class Solution:
    def kthRemainingInteger(self, nums: list[int], queries: list[list[int]]) -> list[int]:
        """
        Interview explanation:
        Remaining positive evens after removing those in nums[l..r]. Work in
        half-space: answer = 2m where m is the k-th positive integer not equal
        to any nums[i]/2 for even nums[i] in the range.

        Algorithm:
        - Prefix count of even values.
        - For each query, binary-search m: m − (# evens in [l,r] with value ≤ 2m) ≥ k.

        Complexity: O((n + q log(k+n)) log n) time, O(n) space.
        """
        n = len(nums)
        prefix = [0] * (n + 1)
        for i, x in enumerate(nums):
            prefix[i + 1] = prefix[i] + (x % 2 == 0)

        ans = []
        for l, r, k in queries:
            lo, hi = k, k + (r - l + 1)
            while lo < hi:
                mid = (lo + hi) // 2
                # evens in [l,r] with nums[i] <= 2*mid
                idx = bisect.bisect_right(nums, 2 * mid, l, r + 1) - 1
                removed = prefix[idx + 1] - prefix[l] if idx >= l else 0
                if mid - removed >= k:
                    hi = mid
                else:
                    lo = mid + 1
            ans.append(2 * lo)
        return ans
# @lc code=end
