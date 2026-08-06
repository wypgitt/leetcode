#
# @lc app=leetcode id=1679 lang=python3
#
# [1679] Max Number of K-Sum Pairs
#
# https://leetcode.com/problems/max-number-of-k-sum-pairs/description/
#
# algorithms
# Medium (57.27%)
# Likes:    3588
# Dislikes: 123
# Total Accepted:    633K
# Total Submissions: 1.1M
# Testcase Example:  "[1,2,3,4]"
#
# You are given an integer array nums and an integer k.
#
# In one operation, you can pick two numbers from the array whose sum equals k
# and remove them from the array.
#
# Return the maximum number of operations you can perform on the array.
#
# Example 1:
#
# Input: nums = [1,2,3,4], k = 5
# Output: 2
# Explanation: Starting with nums = [1,2,3,4]:
# - Remove numbers 1 and 4, then nums = [2,3]
# - Remove numbers 2 and 3, then nums = []
# There are no more pairs that sum up to 5, hence a total of 2 operations.
#
# Example 2:
#
# Input: nums = [3,1,3,4,3], k = 6
# Output: 1
# Explanation: Starting with nums = [3,1,3,4,3]:
# - Remove the first two 3's, then nums = [1,4,3]
# There are no more pairs that sum up to 6, hence a total of 1 operation.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# 1 <= k <= 10^9
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def maxOperations(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Max pairs with sum k; each element used once. Hash counts: for each x
        pair with k-x when available.

        Algorithm (hash map):
        - Count frequencies; for x, take min(cnt[x], cnt[k-x]) carefully for 2x=k.

        Complexity: O(n) time, O(n) space.
        """
        cnt = Counter(nums)
        ans = 0
        for x in list(cnt.keys()):
            y = k - x
            if x < y:
                ans += min(cnt[x], cnt[y])
            elif x == y:
                ans += cnt[x] // 2
        return ans

    def maxOperations_two_pointer(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: sort + two pointers from ends; equal sum → pair; else move.

        Algorithm:
        - Sort; i=0,j=n-1; while i<j: s=nums[i]+nums[j]; adjust.

        Complexity: O(n log n) time, O(1)/O(n) space.
        """
        nums = sorted(nums)
        i, j = 0, len(nums) - 1
        ans = 0
        while i < j:
            s = nums[i] + nums[j]
            if s == k:
                ans += 1
                i += 1
                j -= 1
            elif s < k:
                i += 1
            else:
                j -= 1
        return ans
# @lc code=end
