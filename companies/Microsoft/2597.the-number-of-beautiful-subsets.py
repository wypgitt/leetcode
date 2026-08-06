#
# @lc app=leetcode id=2597 lang=python3
#
# [2597] The Number of Beautiful Subsets
#
# https://leetcode.com/problems/the-number-of-beautiful-subsets/description/
#
# algorithms
# Medium (50.98%)
# Likes:    1321
# Dislikes: 178
# Total Accepted:    134.4K
# Total Submissions: 263.6K
# Testcase Example:  "[2,4,6]\n2"
#
# You are given an array nums of positive integers and a positive integer k.
#
# A subset of nums is beautiful if it does not contain two integers with an
# absolute difference equal to k.
#
# Return the number of non-empty beautiful subsets of the array nums.
#
# A subset of nums is an array that can be obtained by deleting some (possibly
# none) elements from nums. Two subsets are different if and only if the chosen
# indices to delete are different.
#
#
#
# Example 1:
#
# Input: nums = [2,4,6], k = 2
# Output: 4
# Explanation: The beautiful subsets of the array nums are: [2], [4], [6], [2,
# 6].
# It can be proved that there are only 4 beautiful subsets in the array [2,4,6].
#
# Example 2:
#
# Input: nums = [1], k = 1
# Output: 1
# Explanation: The beautiful subset of the array nums is [1].
# It can be proved that there is only 1 beautiful subset in the array [1].
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 18
#
#
# 1 <= nums[i], k <= 1000
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def beautifulSubsets(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Count non-empty subsets with no two elements differing by k.

        Algorithm:
        - Group values by residue mod k; within each residue, values form chains spaced by k.
        - House-robber style DP on each chain using frequencies (2^freq subsets per value).
        - Multiply independent groups; subtract the empty subset.

        Complexity: O(n log n) time, O(n) space.
        """
        cnt = Counter(nums)
        groups = {}
        for v in sorted(cnt):
            groups.setdefault(v % k, []).append(v)

        def ways(vals: List[int]) -> int:
            dp0, dp1 = 1, 0
            prev = None
            for v in vals:
                all_sub = pow(2, cnt[v])
                if prev is not None and v - prev == k:
                    ndp0 = dp0 + dp1
                    ndp1 = dp0 * (all_sub - 1)
                else:
                    ndp0 = dp0 + dp1
                    ndp1 = (dp0 + dp1) * (all_sub - 1)
                dp0, dp1 = ndp0, ndp1
                prev = v
            return dp0 + dp1

        ans = 1
        for vals in groups.values():
            ans *= ways(vals)
        return ans - 1

    def beautifulSubsets_dfs(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Backtracking over the array counting valid subsets (classic interview approach).

        Algorithm:
        - Sort; DFS include/exclude; forbid include when count[x-k] > 0.

        Complexity: O(2^n) time, O(n) space.
        """
        nums = sorted(nums)
        cnt = Counter()
        n = len(nums)

        def dfs(i: int) -> int:
            if i == n:
                return 1
            ans = dfs(i + 1)
            x = nums[i]
            if cnt[x - k] == 0:
                cnt[x] += 1
                ans += dfs(i + 1)
                cnt[x] -= 1
            return ans

        return dfs(0) - 1
# @lc code=end
