#
# @lc app=leetcode id=3040 lang=python3
#
# [3040] Maximum Number of Operations With the Same Score II
#
# https://leetcode.com/problems/maximum-number-of-operations-with-the-same-score-ii/description/
#
# algorithms
# Medium (34.20%)
# Likes:    195
# Dislikes: 16
# Total Accepted:    26.2K
# Total Submissions: 76.7K
# Testcase Example:  "[3,2,1,2,3,4]"
#
#
# Given an array of integers called nums, you can perform any of the
# following operation while nums contains at least 2 elements:
#
# Choose the first two elements of nums and delete them.
#
# Choose the last two elements of nums and delete them.
#
# Choose the first and the last elements of nums and delete them.
#
# The score of the operation is the sum of the deleted elements.
#
# Your task is to find the maximum number of operations that can be
# performed, such that all operations have the same score.
#
# Return the maximum number of operations possible that satisfy the
# condition mentioned above.
#
# Example 1:
#
# Input: nums = [3,2,1,2,3,4]
# Output: 3
# Explanation: We perform the following operations:
# - Delete the first two elements, with score 3 + 2 = 5, nums = [1,2,3,4].
# - Delete the first and the last elements, with score 1 + 4 = 5, nums =
# [2,3].
# - Delete the first and the last elements, with score 2 + 3 = 5, nums =
# [].
# We are unable to perform any more operations as nums is empty.
#
# Example 2:
#
# Input: nums = [3,2,6,1,4]
# Output: 2
# Explanation: We perform the following operations:
# - Delete the first two elements, with score 3 + 2 = 5, nums = [6,1,4].
# - Delete the last two elements, with score 1 + 4 = 5, nums = [6].
# It can be proven that we can perform at most 2 operations.
#
# Constraints:
#
# 2 <= nums.length <= 2000
#
# 1 <= nums[i] <= 1000
#

# @lc code=start

from functools import cache
from typing import List


class Solution:
    def maxOperations(self, nums: List[int]) -> int:
        """
        Interview explanation:
        From either end (or both ends) delete a pair with a fixed score;
        maximize operations. Score is fixed by the first move, so try the
        three possible first-move scores and DP the rest.

        Algorithm:
        - Candidate scores: nums[0]+nums[1], nums[-1]+nums[-2], nums[0]+nums[-1].
        - DP(l,r): max ops on nums[l..r] with the fixed score (memoized).
          Try the three legal pair deletions when they match the score.

        Complexity: O(n^2) time and space (n<=2000).
        """
        n = len(nums)
        best = 0
        for score in {nums[0] + nums[1], nums[-1] + nums[-2], nums[0] + nums[-1]}:

            @cache
            def dp(l: int, r: int) -> int:
                if r - l + 1 < 2:
                    return 0
                ans = 0
                if nums[l] + nums[l + 1] == score:
                    ans = max(ans, 1 + dp(l + 2, r))
                if nums[r - 1] + nums[r] == score:
                    ans = max(ans, 1 + dp(l, r - 2))
                if nums[l] + nums[r] == score:
                    ans = max(ans, 1 + dp(l + 1, r - 1))
                return ans

            best = max(best, dp(0, n - 1))
            dp.cache_clear()
        return best
# @lc code=end
