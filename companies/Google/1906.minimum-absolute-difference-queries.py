#
# @lc app=leetcode id=1906 lang=python3
#
# [1906] Minimum Absolute Difference Queries
#
# https://leetcode.com/problems/minimum-absolute-difference-queries/description/
#
# algorithms
# Medium (45.96%)
# Likes:    558
# Dislikes: 46
# Total Accepted:    14.4K
# Total Submissions: 31.3K
# Testcase Example:  "[1,3,4,8]"
#
# The minimum absolute difference of an array a is defined as the minimum value
# of |a[i] - a[j]|, where 0 <= i < j < a.length and a[i] != a[j]. If all
# elements of a are the same, the minimum absolute difference is -1.
#
# For example, the minimum absolute difference of the array [5,2,3,7,2] is |2 -
# 3| = 1. Note that it is not 0 because a[i] and a[j] must be different.
#
# You are given an integer array nums and the array queries where queries[i] =
# [l_i, r_i]. For each query i, compute the minimum absolute difference of the
# subarray nums[l_i...r_i] containing the elements of nums between the 0-based
# indices l_i and r_i (inclusive).
#
# Return an array ans where ans[i] is the answer to the i^th query.
#
# A subarray is a contiguous sequence of elements in an array.
#
# The value of |x| is defined as:
#
# x if x >= 0.
#
# -x if x < 0.
#
# Example 1:
#
# Input: nums = [1,3,4,8], queries = [[0,1],[1,2],[2,3],[0,3]]
# Output: [2,1,4,1]
# Explanation: The queries are processed as follows:
# - queries[0] = [0,1]: The subarray is [1,3] and the minimum absolute
# difference is |1-3| = 2.
# - queries[1] = [1,2]: The subarray is [3,4] and the minimum absolute
# difference is |3-4| = 1.
# - queries[2] = [2,3]: The subarray is [4,8] and the minimum absolute
# difference is |4-8| = 4.
# - queries[3] = [0,3]: The subarray is [1,3,4,8] and the minimum absolute
# difference is |3-4| = 1.
#
# Example 2:
#
# Input: nums = [4,5,2,2,7,10], queries = [[2,3],[0,2],[0,5],[3,5]]
# Output: [-1,1,1,3]
# Explanation: The queries are processed as follows:
# - queries[0] = [2,3]: The subarray is [2,2] and the minimum absolute
# difference is -1 because all the
# elements are the same.
# - queries[1] = [0,2]: The subarray is [4,5,2] and the minimum absolute
# difference is |4-5| = 1.
# - queries[2] = [0,5]: The subarray is [4,5,2,2,7,10] and the minimum absolute
# difference is |4-5| = 1.
# - queries[3] = [3,5]: The subarray is [2,7,10] and the minimum absolute
# difference is |7-10| = 3.
#
# Constraints:
#
# 2 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 100
#
# 1 <= queries.length <= 2 * 10^4
#
# 0 <= l_i < r_i < nums.length
#

# @lc code=start
from typing import List


class Solution:
    def minDifference(self, nums: List[int], queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        For each query [l,r], min |a-b| over distinct values in nums[l..r], or -1.
        Values are in 1..100 → prefix counts per value; reconstruct sorted unique
        set per query and scan adjacent gaps.

        Algorithm:
        - pref[i][v] = count of v in nums[:i]. For query, collect v with positive
          count; min adjacent difference among sorted uniques.

        Complexity: O((n+q)*V) time, O(nV) space, V=100.
        """
        V = 100
        n = len(nums)
        pref = [[0] * (V + 1) for _ in range(n + 1)]
        for i, x in enumerate(nums):
            pref[i + 1] = pref[i][:]
            pref[i + 1][x] += 1
        ans = []
        for l, r in queries:
            vals = [v for v in range(1, V + 1) if pref[r + 1][v] - pref[l][v] > 0]
            if len(vals) < 2:
                ans.append(-1)
            else:
                ans.append(min(vals[i + 1] - vals[i] for i in range(len(vals) - 1)))
        return ans
# @lc code=end
