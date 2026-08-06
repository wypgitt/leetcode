#
# @lc app=leetcode id=1498 lang=python3
#
# [1498] Number of Subsequences That Satisfy the Given Sum Condition
#
# https://leetcode.com/problems/number-of-subsequences-that-satisfy-the-given-sum-condition/description/
#
# algorithms
# Medium (49.04%)
# Likes:    4706
# Dislikes: 437
# Total Accepted:    257K
# Total Submissions: 524K
# Testcase Example:  "[3,5,6,7]"
#
# You are given an array of integers nums and an integer target.
#
# Return the number of non-empty subsequences of nums such that the sum of the
# minimum and maximum element on it is less or equal to target. Since the
# answer may be too large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: nums = [3,5,6,7], target = 9
# Output: 4
# Explanation: There are 4 subsequences that satisfy the condition.
# [3] -> Min value + max value <= target (3 + 3 <= 9)
# [3,5] -> (3 + 5 <= 9)
# [3,5,6] -> (3 + 6 <= 9)
# [3,6] -> (3 + 6 <= 9)
#
# Example 2:
#
# Input: nums = [3,3,6,8], target = 10
# Output: 6
# Explanation: There are 6 subsequences that satisfy the condition. (nums can
# have repeated numbers).
# [3] , [3] , [3,3], [3,6] , [3,6] , [3,3,6]
#
# Example 3:
#
# Input: nums = [2,3,3,4,6,7], target = 12
# Output: 61
# Explanation: There are 63 non-empty subsequences, two of them do not satisfy
# the condition ([6,7], [7]).
# Number of valid subsequences (63 - 2 = 61).
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^6
#
# 1 <= target <= 10^6
#

# @lc code=start
from typing import List


class Solution:
    def numSubseq(self, nums: List[int], target: int) -> int:
        """
        Interview explanation:
        Count non-empty subsequences where min+max <= target. Sort; for each
        left as minimum, binary-search rightmost max feasible; all subsets of
        the middle contribute 2^(r-l).

        Algorithm:
        - Sort; two pointers / bisect; precompute pow2; MOD=1e9+7.

        Complexity: O(n log n) time, O(n) space for powers.
        """
        MOD = 10**9 + 7
        nums.sort()
        n = len(nums)
        pow2 = [1] * n
        for i in range(1, n):
            pow2[i] = (pow2[i - 1] * 2) % MOD
        ans = 0
        lo, hi = 0, n - 1
        while lo <= hi:
            if nums[lo] + nums[hi] <= target:
                ans = (ans + pow2[hi - lo]) % MOD
                lo += 1
            else:
                hi -= 1
        return ans

    def numSubseq_bisect(self, nums: List[int], target: int) -> int:
        """
        Interview explanation:
        Alternate: for each i as min, bisect_right for target-nums[i].

        Algorithm:
        - Sort; precompute pow2; for i, j=bisect; if j>i add 2^(j-i-1).

        Complexity: O(n log n) time, O(n) space.
        """
        import bisect

        MOD = 10**9 + 7
        nums.sort()
        n = len(nums)
        pow2 = [1] * (n + 1)
        for i in range(1, n + 1):
            pow2[i] = (pow2[i - 1] * 2) % MOD
        ans = 0
        for i, x in enumerate(nums):
            if 2 * x > target:
                break
            j = bisect.bisect_right(nums, target - x) - 1
            if j >= i:
                ans = (ans + pow2[j - i]) % MOD
        return ans
# @lc code=end
