#
# @lc app=leetcode id=3748 lang=python3
#
# [3748] Count Stable Subarrays
#
# https://leetcode.com/problems/count-stable-subarrays/description/
#
# algorithms
# Hard (33.10%)
# Likes:    68
# Dislikes: 2
# Total Accepted:    6.5K
# Total Submissions: 19.5K
# Testcase Example:  "[3,1,2]\n[[0,1],[1,2],[0,2]]"
#
#
# You are given an integer array nums.
#
# A subarray of nums is called stable if it contains no inversions, i.e.,
# there is no pair of indices i < j such that nums[i] > nums[j].
#
# You are also given a 2D integer array queries of length q, where each
# queries[i] = [l_i, r_i] represents a query. For each query [l_i, r_i],
# compute the number of stable subarrays that lie entirely within the
# segment nums[l_i..r_i].
#
# Return an integer array ans of length q, where ans[i] is the answer to
# the i^th query.​​​​​​​​​​​​​​
#
# Note:
#
# A single element subarray is considered stable.
#
# Example 1:
#
# Input: nums = [3,1,2], queries = [[0,1],[1,2],[0,2]]
#
# Output: [2,3,4]
#
# Explanation:​​​​​
#
# For queries[0] = [0, 1], the subarray is [nums[0], nums[1]] = [3, 1].
#
# The stable subarrays are [3] and [1]. The total number of stable
# subarrays is 2.
#
# For queries[1] = [1, 2], the subarray is [nums[1], nums[2]] = [1, 2].
#
# The stable subarrays are [1], [2], and [1, 2]. The total number of
# stable subarrays is 3.
#
# For queries[2] = [0, 2], the subarray is [nums[0], nums[1], nums[2]] =
# [3, 1, 2].
#
# The stable subarrays are [3], [1], [2], and [1, 2]. The total number of
# stable subarrays is 4.
#
# Thus, ans = [2, 3, 4].
#
# Example 2:
#
# Input: nums = [2,2], queries = [[0,1],[0,0]]
#
# Output: [3,1]
#
# Explanation:
#
# For queries[0] = [0, 1], the subarray is [nums[0], nums[1]] = [2, 2].
#
# The stable subarrays are [2], [2], and [2, 2]. The total number of
# stable subarrays is 3.
#
# For queries[1] = [0, 0], the subarray is [nums[0]] = [2].
#
# The stable subarray is [2]. The total number of stable subarrays is 1.
#
# Thus, ans = [3, 1].
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#
# 1 <= queries.length <= 10^5
#
# queries[i] = [l_i, r_i]
#
# 0 <= l_i <= r_i <= nums.length - 1
#

# @lc code=start
from typing import List


class Solution:
    def countStableSubarrays(self, nums: List[int], queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Stable means non-decreasing. Inside a maximal non-decreasing run of length
        L there are L*(L+1)/2 stable subarrays. Answer range queries with run ends
        and prefix sums of per-ending counts.

        Algorithm:
        - right[i] = farthest end of a non-decreasing subarray starting at i.
        - prefix[i+1] = total stable subarrays in nums[0..i].
        - For [l, r]: take the full triangle on [l..min(right[l], r)], then add
          prefix[r+1] - prefix[min(right[l], r)+1] for later starts.

        Complexity: O(n + q) time, O(n) space.
        """
        n = len(nums)
        right = list(range(n))
        for i in range(n - 2, -1, -1):
            if nums[i] <= nums[i + 1]:
                right[i] = right[i + 1]

        prefix = [0] * (n + 1)
        curr = 0
        for i in range(n):
            if i > 0 and nums[i - 1] > nums[i]:
                curr = 0
            curr += 1
            prefix[i + 1] = prefix[i] + curr

        def triangle(length: int) -> int:
            return length * (length + 1) // 2

        ans = []
        for l, r in queries:
            p = min(right[l], r)
            ans.append(triangle(p - l + 1) + (prefix[r + 1] - prefix[p + 1]))
        return ans
# @lc code=end
