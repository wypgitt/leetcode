#
# @lc app=leetcode id=3277 lang=python3
#
# [3277] Maximum XOR Score Subarray Queries
#
# https://leetcode.com/problems/maximum-xor-score-subarray-queries/description/
#
# algorithms
# Hard (43.93%)
# Likes:    111
# Dislikes: 17
# Total Accepted:    5.9K
# Total Submissions: 13.4K
# Testcase Example:  "[2,8,4,32,16,1]\n[[0,2],[1,4],[0,5]]"
#
#
# You are given an array nums of n integers, and a 2D integer array
# queries of size q, where queries[i] = [l_i, r_i].
#
# For each query, you must find the maximum XOR score of any subarray of
# nums[l_i..r_i].
#
# The XOR score of an array a is found by repeatedly applying the
# following operations on a so that only one element remains, that is the
# score:
#
# Simultaneously replace a[i] with a[i] XOR a[i + 1] for all indices i
# except the last one.
#
# Remove the last element of a.
#
# Return an array answer of size q where answer[i] is the answer to query
# i.
#
# Example 1:
#
# Input: nums = [2,8,4,32,16,1], queries = [[0,2],[1,4],[0,5]]
#
# Output: [12,60,60]
#
# Explanation:
#
# In the first query, nums[0..2] has 6 subarrays [2], [8], [4], [2, 8],
# [8, 4], and [2, 8, 4] each with a respective XOR score of 2, 8, 4, 10,
# 12, and 6. The answer for the query is 12, the largest of all XOR
# scores.
#
# In the second query, the subarray of nums[1..4] with the largest XOR
# score is nums[1..4] with a score of 60.
#
# In the third query, the subarray of nums[0..5] with the largest XOR
# score is nums[1..4] with a score of 60.
#
# Example 2:
#
# Input: nums = [0,7,3,2,8,5,1], queries = [[0,3],[1,5],[2,4],[2,6],[5,6]]
#
# Output: [7,14,11,14,5]
#
# Explanation:
#
#                         Index
#                         nums[l_i..r_i]
#                         Maximum XOR Score Subarray
#                         Maximum Subarray XOR Score
#
#                         0
#                         [0, 7, 3, 2]
#                         [7]
#                         7
#
#                         1
#                         [7, 3, 2, 8, 5]
#                         [7, 3, 2, 8]
#                         14
#
#                         2
#                         [3, 2, 8]
#                         [3, 2, 8]
#                         11
#
#                         3
#                         [3, 2, 8, 5, 1]
#                         [2, 8, 5, 1]
#                         14
#
#                         4
#                         [5, 1]
#                         [5]
#                         5
#
# Constraints:
#
# 1 <= n == nums.length <= 2000
#
# 0 <= nums[i] <= 2^31 - 1
#
# 1 <= q == queries.length <= 10^5
#
# queries[i].length == 2
#
# queries[i] = [l_i, r_i]
#
# 0 <= l_i <= r_i <= n - 1
#

# @lc code=start

from typing import List


class Solution:
    def maximumSubarrayXor(self, nums: List[int], queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        XOR-score of a subarray collapses by pairwise XORs; it obeys
        score[i][j] = score[i][j-1] XOR score[i+1][j]. The answer on [L,R] is the
        max score over all subarrays inside — fillable by interval DP.

        Algorithm:
        - score[i][i] = nums[i]; for len≥2: score[i][j] = score[i][j-1] ^ score[i+1][j].
        - mx[i][j] = max(score[i][j], mx[i][j-1], mx[i+1][j]).
        - Answer each query with mx[l][r].

        Complexity: O(n^2 + q) time, O(n^2) space.
        """
        n = len(nums)
        score = [[0] * n for _ in range(n)]
        mx = [[0] * n for _ in range(n)]
        for i in range(n):
            score[i][i] = nums[i]
            mx[i][i] = nums[i]
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                score[i][j] = score[i][j - 1] ^ score[i + 1][j]
                mx[i][j] = max(score[i][j], mx[i][j - 1], mx[i + 1][j])
        return [mx[l][r] for l, r in queries]
# @lc code=end
