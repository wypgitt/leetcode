#
# @lc app=leetcode id=719 lang=python3
#
# [719] Find K-th Smallest Pair Distance
#
# https://leetcode.com/problems/find-k-th-smallest-pair-distance/description/
#
# algorithms
# Hard (46.72%)
# Likes:    3974
# Dislikes: 126
# Total Accepted:    218K
# Total Submissions: 466K
# Testcase Example:  "[1,3,1]"
#
# The distance of a pair of integers a and b is defined as the absolute
# difference between a and b.
#
# Given an integer array nums and an integer k, return the k^th smallest
# distance among all the pairs nums[i] and nums[j] where 0 <= i < j <
# nums.length.
#
# Example 1:
#
# Input: nums = [1,3,1], k = 1
# Output: 0
# Explanation: Here are all the pairs:
# (1,3) -> 2
# (1,1) -> 0
# (3,1) -> 2
# Then the 1^st smallest distance pair is (1,1), and its distance is 0.
#
# Example 2:
#
# Input: nums = [1,1,1], k = 2
# Output: 0
#
# Example 3:
#
# Input: nums = [1,6,1], k = 3
# Output: 5
#
# Constraints:
#
# n == nums.length
#
# 2 <= n <= 10^4
#
# 0 <= nums[i] <= 10^6
#
# 1 <= k <= n * (n - 1) / 2
#

# @lc code=start
from typing import List


class Solution:
    def smallestDistancePair(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        K-th smallest absolute pair distance. Sort, then binary search the
        distance D: count pairs with distance <= D via two pointers; find
        minimal D with count >= k.

        Algorithm:
        - Sort nums. lo=0, hi=max-min. While lo<hi: mid; if count(mid)>=k hi=mid
          else lo=mid+1. count: for right, advance left while nums[right]-nums[left]>mid;
          add right-left.

        Complexity: O(n log n + n log W) time, O(1)/O(n) space.
        """
        nums.sort()
        n = len(nums)

        def count(mid: int) -> int:
            cnt = left = 0
            for right in range(n):
                while nums[right] - nums[left] > mid:
                    left += 1
                cnt += right - left
            return cnt

        lo, hi = 0, nums[-1] - nums[0]
        while lo < hi:
            mid = (lo + hi) // 2
            if count(mid) >= k:
                hi = mid
            else:
                lo = mid + 1
        return lo
# @lc code=end
