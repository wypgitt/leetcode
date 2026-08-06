#
# @lc app=leetcode id=3018 lang=python3
#
# [3018] Maximum Number of Removal Queries That Can Be Processed I
#
# https://leetcode.com/problems/maximum-number-of-removal-queries-that-can-be-processed-i/description/
#
# algorithms
# Hard (44.63%)
# Likes:    7
# Dislikes: 3
# Total Accepted:    681
# Total Submissions: 1.5K
# Testcase Example:  "[1,2,3,4,5]\n[1,2,3,4,6]"
#
#
# You are given a 0-indexed array nums and a 0-indexed array queries.
#
# You can do the following operation at the beginning at most once:
#
# Replace nums with a subsequence of nums.
#
# We start processing queries in the given order; for each query, we do
# the following:
#
# If the first and the last element of nums is less than queries[i], the
# processing of queries ends.
#
# Otherwise, we choose either the first or the last element of nums if it
# is greater than or equal to queries[i], and we remove the chosen element
# from nums.
#
# Return the maximum number of queries that can be processed by doing the
# operation optimally.
#
# Example 1:
#
# Input: nums = [1,2,3,4,5], queries = [1,2,3,4,6]
# Output: 4
# Explanation: We don't do any operation and process the queries as
# follows:
# 1- We choose and remove nums[0] since 1 <= 1, then nums becomes
# [2,3,4,5].
# 2- We choose and remove nums[0] since 2 <= 2, then nums becomes [3,4,5].
# 3- We choose and remove nums[0] since 3 <= 3, then nums becomes [4,5].
# 4- We choose and remove nums[0] since 4 <= 4, then nums becomes [5].
# 5- We can not choose any elements from nums since they are not greater
# than or equal to 5.
# Hence, the answer is 4.
# It can be shown that we can't process more than 4 queries.
#
# Example 2:
#
# Input: nums = [2,3,2], queries = [2,2,3]
# Output: 3
# Explanation: We don't do any operation and process the queries as
# follows:
# 1- We choose and remove nums[0] since 2 <= 2, then nums becomes [3,2].
# 2- We choose and remove nums[1] since 2 <= 2, then nums becomes [3].
# 3- We choose and remove nums[0] since 3 <= 3, then nums becomes [].
# Hence, the answer is 3.
# It can be shown that we can't process more than 3 queries.
#
# Example 3:
#
# Input: nums = [3,4,3], queries = [4,3,2]
# Output: 2
# Explanation: First we replace nums with the subsequence of nums [4,3].
# Then we can process the queries as follows:
# 1- We choose and remove nums[0] since 4 <= 4, then nums becomes [3].
# 2- We choose and remove nums[0] since 3 <= 3, then nums becomes [].
# 3- We can not process any more queries since nums is empty.
# Hence, the answer is 2.
# It can be shown that we can't process more than 2 queries.
#
# Constraints:
#
# 1 <= nums.length <= 1000
#
# 1 <= queries.length <= 1000
#
# 1 <= nums[i], queries[i] <= 10^9
#

# @lc code=start

from typing import List


class Solution:
    def maximumProcessableQueries(self, nums: List[int], queries: List[int]) -> int:
        """
        Interview explanation:
        Optionally replace nums by a contiguous subarray (optimal subsequence),
        then repeatedly delete an end >= next query. DP tracks how many queries
        are finished when the yet-undeleted middle is [i, j].

        Algorithm:
        - f[i][j] = max queries processed with remaining segment nums[i..j].
        - Transition from f[i-1][j] / f[i][j+1] by deleting the just-excluded
          outer element if it satisfies the next query (or skip via the initial
          subsequence, modeled by base 0).
        - Answer is max over i of f[i][i] plus optionally deleting nums[i].

        Complexity: O(n^2) time, O(n^2) space.
        """
        n, m = len(nums), len(queries)
        f = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n - 1, i - 1, -1):
                if i:
                    qi = f[i - 1][j]
                    f[i][j] = max(
                        f[i][j], qi + (1 if qi < m and nums[i - 1] >= queries[qi] else 0)
                    )
                if j + 1 < n:
                    qi = f[i][j + 1]
                    f[i][j] = max(
                        f[i][j], qi + (1 if qi < m and nums[j + 1] >= queries[qi] else 0)
                    )
                if f[i][j] == m:
                    return m
        ans = 0
        for i in range(n):
            qi = f[i][i]
            ans = max(ans, qi + (1 if qi < m and nums[i] >= queries[qi] else 0))
        return ans
# @lc code=end
