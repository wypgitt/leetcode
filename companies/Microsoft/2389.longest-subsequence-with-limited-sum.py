#
# @lc app=leetcode id=2389 lang=python3
#
# [2389] Longest Subsequence With Limited Sum
#
# https://leetcode.com/problems/longest-subsequence-with-limited-sum/description/
#
# algorithms
# Easy (73.74%)
# Likes:    2172
# Dislikes: 198
# Total Accepted:    173.1K
# Total Submissions: 234.7K
# Testcase Example:  "[4,5,2,1]\n[3,10,21]"
#
# You are given an integer array nums of length n, and an integer array queries
# of length m.
#
# Return an array answer of length m where answer[i] is the maximum size of a
# subsequence that you can take from nums such that the sum of its elements is
# less than or equal to queries[i].
#
# A subsequence is an array that can be derived from another array by deleting
# some or no elements without changing the order of the remaining elements.
#
#
#
# Example 1:
#
# Input: nums = [4,5,2,1], queries = [3,10,21]
# Output: [2,3,4]
# Explanation: We answer the queries as follows:
# - The subsequence [2,1] has a sum less than or equal to 3. It can be proven
# that 2 is the maximum size of such a subsequence, so answer[0] = 2.
# - The subsequence [4,5,1] has a sum less than or equal to 10. It can be proven
# that 3 is the maximum size of such a subsequence, so answer[1] = 3.
# - The subsequence [4,5,2,1] has a sum less than or equal to 21. It can be
# proven that 4 is the maximum size of such a subsequence, so answer[2] = 4.
#
# Example 2:
#
# Input: nums = [2,3,4,5], queries = [1]
# Output: [0]
# Explanation: The empty subsequence is the only subsequence that has a sum less
# than or equal to 1, so answer[0] = 0.
#
#
#
# Constraints:
#
#
# n == nums.length
#
#
# m == queries.length
#
#
# 1 <= n, m <= 1000
#
#
# 1 <= nums[i], queries[i] <= 10^6
#

# @lc code=start

from typing import List
from bisect import bisect_right
import itertools


class Solution:
    def answerQueries(self, nums: List[int], queries: List[int]) -> List[int]:
        """
        Interview explanation:
        For each query q, max size of a subsequence of nums with sum <= q.

        Algorithm:
        - Sort nums ascending (smallest elements maximize count); prefix sums;
          binary search largest prefix <= q.

        Complexity: O(n log n + m log n) time, O(n) space.
        """
        nums.sort()
        pref = list(itertools.accumulate(nums))
        return [bisect_right(pref, q) for q in queries]

    def answerQueries_binary_search(self, nums: List[int], queries: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate: explicit binary search per query on prefix sums.

        Algorithm:
        - Same sort + prefix; manual lo/hi for each query.

        Complexity: O(n log n + m log n) time, O(n) space.
        """
        nums.sort()
        n = len(nums)
        pref = [0] * n
        s = 0
        for i, x in enumerate(nums):
            s += x
            pref[i] = s
        ans = []
        for q in queries:
            lo, hi = 0, n
            while lo < hi:
                mid = (lo + hi) // 2
                if pref[mid] <= q:
                    lo = mid + 1
                else:
                    hi = mid
            ans.append(lo)
        return ans
# @lc code=end
