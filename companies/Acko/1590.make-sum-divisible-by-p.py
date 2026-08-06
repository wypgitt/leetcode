#
# @lc app=leetcode id=1590 lang=python3
#
# [1590] Make Sum Divisible by P
#
# https://leetcode.com/problems/make-sum-divisible-by-p/description/
#
# algorithms
# Medium (42.6%)
# Likes:    2913
# Dislikes: 198
# Total Accepted:    234K
# Total Submissions: 550K
# Testcase Example:  "[3,1,4,2]"
#
# Given an array of positive integers nums, remove the smallest subarray
# (possibly empty) such that the sum of the remaining elements is divisible by
# p. It is not allowed to remove the whole array.
#
# Return the length of the smallest subarray that you need to remove, or -1 if
# it's impossible.
#
# A subarray is defined as a contiguous block of elements in the array.
#
# Example 1:
#
# Input: nums = [3,1,4,2], p = 6
# Output: 1
# Explanation: The sum of the elements in nums is 10, which is not divisible by
# 6. We can remove the subarray [4], and the sum of the remaining elements is
# 6, which is divisible by 6.
#
# Example 2:
#
# Input: nums = [6,3,5,2], p = 9
# Output: 2
# Explanation: We cannot remove a single element to get a sum divisible by 9.
# The best way is to remove the subarray [5,2], leaving us with [6,3] with sum
# 9.
#
# Example 3:
#
# Input: nums = [1,2,3], p = 3
# Output: 0
# Explanation: Here the sum is 6. which is already divisible by 3. Thus we do
# not need to remove anything.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# 1 <= p <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def minSubarray(self, nums: List[int], p: int) -> int:
        """
        Interview explanation:
        Remove shortest contiguous subarray so remaining sum ≡ 0 (mod p).
        Need subarray sum ≡ total % p. Prefix mod + last-seen index map for
        target = (prefix - need) mod p.

        Algorithm:
        - need = sum(nums) % p; if 0 return 0.
        - last[0]=-1; for i,x: prefix=(prefix+x)%p; want=(prefix-need)%p;
          if want in last: ans=min(ans, i-last[want]); last[prefix]=i.
        - If ans==n return -1.

        Complexity: O(n) time, O(min(n,p)) space.
        """
        need = sum(nums) % p
        if need == 0:
            return 0
        last = {0: -1}
        prefix = 0
        ans = n = len(nums)
        for i, x in enumerate(nums):
            prefix = (prefix + x) % p
            want = (prefix - need) % p
            if want in last:
                ans = min(ans, i - last[want])
            last[prefix] = i
        return -1 if ans == n else ans
# @lc code=end

