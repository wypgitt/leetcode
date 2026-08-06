#
# @lc app=leetcode id=2826 lang=python3
#
# [2826] Sorting Three Groups
#
# https://leetcode.com/problems/sorting-three-groups/description/
#
# algorithms
# Medium (43.28%)
# Likes:    530
# Dislikes: 93
# Total Accepted:    27.6K
# Total Submissions: 63.7K
# Testcase Example:  "[2,1,3,2,1]"
#
#
# You are given an integer array nums. Each element in nums is 1, 2 or 3.
# In each operation, you can remove an element from nums. Return the
# minimum number of operations to make nums non-decreasing.
#
# Example 1:
#
# Input: nums = [2,1,3,2,1]
#
# Output: 3
#
# Explanation:
#
# One of the optimal solutions is to remove nums[0], nums[2] and nums[3].
#
# Example 2:
#
# Input: nums = [1,3,2,1,3,3]
#
# Output: 2
#
# Explanation:
#
# One of the optimal solutions is to remove nums[1] and nums[2].
#
# Example 3:
#
# Input: nums = [2,2,2,2,3,3]
#
# Output: 0
#
# Explanation:
#
# nums is already non-decreasing.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 1 <= nums[i] <= 3
#
# Follow-up: Can you come up with an algorithm that runs in O(n) time
# complexity?
#

# @lc code=start
from typing import List


class Solution:
    def minimumOperations(self, nums: List[int]) -> int:
        """
        Interview explanation:
        nums[i] in {1,2,3}. Min deletions so the remaining array is
        non-decreasing (equivalently n - LDS length of non-decreasing subseq).

        Algorithm:
        - 3-state DP: for each x, f[x] = 1 + max(f[v] for v <= x).
        - Answer = n - max(f).

        Complexity: O(n) time, O(1) space.
        """
        f = [0, 0, 0, 0]
        for x in nums:
            f[x] = max(f[1 : x + 1]) + 1
        return len(nums) - max(f)

    def minimumOperations_splits(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: final sequence is some 1s then 2s then 3s; enumerate the
        two split indices and count how many already match those groups.

        Algorithm:
        - Prefix counts; try all boundaries (i, j); minimize deletions.

        Complexity: O(n^2) time, O(n) space.
        """
        n = len(nums)
        cnt = [[0, 0, 0, 0] for _ in range(n + 1)]
        for i, x in enumerate(nums):
            cnt[i + 1] = cnt[i][:]
            cnt[i + 1][x] += 1
        ans = n
        for i in range(n + 1):
            for j in range(i, n + 1):
                keep = cnt[i][1] + (cnt[j][2] - cnt[i][2]) + (cnt[n][3] - cnt[j][3])
                ans = min(ans, n - keep)
        return ans
# @lc code=end
