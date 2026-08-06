#
# @lc app=leetcode id=2615 lang=python3
#
# [2615] Sum of Distances
#
# https://leetcode.com/problems/sum-of-distances/description/
#
# algorithms
# Medium (50.29%)
# Likes:    1271
# Dislikes: 129
# Total Accepted:    115.1K
# Total Submissions: 228.9K
# Testcase Example:  "[1,3,1,1,2]"
#
# You are given a 0-indexed integer array nums. There exists an array arr of
# length nums.length, where arr[i] is the sum of |i - j| over all j such that
# nums[j] == nums[i] and j != i. If there is no such j, set arr[i] to be 0.
#
# Return the array arr.
#
#
#
# Example 1:
#
# Input: nums = [1,3,1,1,2]
# Output: [5,0,3,4,0]
# Explanation:
# When i = 0, nums[0] == nums[2] and nums[0] == nums[3]. Therefore, arr[0] = |0
# - 2| + |0 - 3| = 5.
# When i = 1, arr[1] = 0 because there is no other index with value 3.
# When i = 2, nums[2] == nums[0] and nums[2] == nums[3]. Therefore, arr[2] = |2
# - 0| + |2 - 3| = 3.
# When i = 3, nums[3] == nums[0] and nums[3] == nums[2]. Therefore, arr[3] = |3
# - 0| + |3 - 2| = 4.
# When i = 4, arr[4] = 0 because there is no other index with value 2.
#
# Example 2:
#
# Input: nums = [0,5,3]
# Output: [0,0,0]
# Explanation: Since each element in nums is distinct, arr[i] = 0 for all i.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 0 <= nums[i] <= 10^9
#
#
#
# Note: This question is the same as  2121: Intervals Between Identical
# Elements.
#

# @lc code=start
from typing import List
from collections import defaultdict


class Solution:
    def distance(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        For each index i, sum |i - j| over all j with nums[j] == nums[i], j != i.

        Algorithm:
        - Group indices by value (already sorted by scan order).
        - For a group idx[0..m), with prefix sums of indices:
          for position t, left = t*idx[t] - pref[t],
          right = (pref[m]-pref[t+1]) - (m-1-t)*idx[t].

        Complexity: O(n) time, O(n) space.
        """
        groups: dict[int, List[int]] = defaultdict(list)
        for i, v in enumerate(nums):
            groups[v].append(i)

        ans = [0] * len(nums)
        for idxs in groups.values():
            m = len(idxs)
            if m == 1:
                continue
            pref = [0] * (m + 1)
            for t in range(m):
                pref[t + 1] = pref[t] + idxs[t]
            total = pref[m]
            for t, i in enumerate(idxs):
                left = t * i - pref[t]
                right = (total - pref[t + 1]) - (m - 1 - t) * i
                ans[i] = left + right
        return ans
# @lc code=end
