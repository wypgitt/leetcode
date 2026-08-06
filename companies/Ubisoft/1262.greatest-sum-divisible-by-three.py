#
# @lc app=leetcode id=1262 lang=python3
#
# [1262] Greatest Sum Divisible by Three
#
# https://leetcode.com/problems/greatest-sum-divisible-by-three/description/
#
# algorithms
# Medium (56.99%)
# Likes:    2441
# Dislikes: 65
# Total Accepted:    168K
# Total Submissions: 295K
# Testcase Example:  "[3,6,5,1,8]"
#
# Given an integer array nums, return the maximum possible sum of elements of
# the array such that it is divisible by three.
#
# Example 1:
#
# Input: nums = [3,6,5,1,8]
# Output: 18
# Explanation: Pick numbers 3, 6, 1 and 8 their sum is 18 (maximum sum
# divisible by 3).
#
# Example 2:
#
# Input: nums = [4]
# Output: 0
# Explanation: Since 4 is not divisible by 3, do not pick any number.
#
# Example 3:
#
# Input: nums = [1,2,3,4,4]
# Output: 12
# Explanation: Pick numbers 1, 3, 4 and 4 their sum is 12 (maximum sum
# divisible by 3).
#
# Constraints:
#
# 1 <= nums.length <= 4 * 10^4
#
# 1 <= nums[i] <= 10^4
#

# @lc code=start

from typing import List


class Solution:
    def maxSumDivThree(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Maximize subset sum divisible by 3. Track best sums for each residue
        mod 3; for each num update the three residues (knapsack style).

        Algorithm:
        - dp=[0,-inf,-inf] meaning best sum ≡ r (mod 3).
        - For x in nums: ndp=dp[:]; for s in dp: ndp[(s+x)%3]=max(..., s+x).
        - Return dp[0].

        Complexity: O(n) time, O(1) space.
        """
        INF = 10**18
        dp = [0, -INF, -INF]
        for x in nums:
            ndp = dp[:]
            for s in dp:
                if s <= -INF // 2:
                    continue
                r = (s + x) % 3
                ndp[r] = max(ndp[r], s + x)
            dp = ndp
        return dp[0]

    def maxSumDivThree_remove(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: total sum; if sum%3==0 done; else remove smallest num with
        that residue, or two smallest of the other residue.

        Algorithm:
        - Compute total; collect nums by mod; if need remove, try min options.

        Complexity: O(n) time, O(n) space.
        """
        total = sum(nums)
        if total % 3 == 0:
            return total
        ones = sorted(x for x in nums if x % 3 == 1)
        twos = sorted(x for x in nums if x % 3 == 2)
        ans = 0
        if total % 3 == 1:
            if ones:
                ans = max(ans, total - ones[0])
            if len(twos) >= 2:
                ans = max(ans, total - twos[0] - twos[1])
        else:
            if twos:
                ans = max(ans, total - twos[0])
            if len(ones) >= 2:
                ans = max(ans, total - ones[0] - ones[1])
        return ans
# @lc code=end
