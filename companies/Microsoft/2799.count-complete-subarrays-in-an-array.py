#
# @lc app=leetcode id=2799 lang=python3
#
# [2799] Count Complete Subarrays in an Array
#
# https://leetcode.com/problems/count-complete-subarrays-in-an-array/description/
#
# algorithms
# Medium (76.08%)
# Likes:    1157
# Dislikes: 28
# Total Accepted:    176.3K
# Total Submissions: 231.7K
# Testcase Example:  "[1,3,1,2,2]"
#
# You are given an array nums consisting of positive integers.
#
# We call a subarray of an array complete if the following condition is
# satisfied:
#
#
# The number of distinct elements in the subarray is equal to the number of
# distinct elements in the whole array.
#
# Return the number of complete subarrays.
#
# A subarray is a contiguous non-empty part of an array.
#
#
#
# Example 1:
#
# Input: nums = [1,3,1,2,2]
# Output: 4
# Explanation: The complete subarrays are the following: [1,3,1,2], [1,3,1,2,2],
# [3,1,2] and [3,1,2,2].
#
# Example 2:
#
# Input: nums = [5,5,5,5]
# Output: 10
# Explanation: The array consists only of the integer 5, so any subarray is
# complete. The number of subarrays that we can choose is 10.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 1000
#
#
# 1 <= nums[i] <= 2000
#

# @lc code=start
from collections import Counter
from typing import List


class Solution:
    def countCompleteSubarrays(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Complete subarray: contains all distinct values present in nums. Count them.

        Algorithm:
        - Two pointers: shrink/expand so window has all distinct; for each right,
          all left..right starts through current left work... equivalently:
          find minimal left such that [left,right] is complete; then all starts
          in [0,left] form complete subarrays ending at right.

        Complexity: O(n) time, O(n) space.
        """
        need = len(set(nums))
        cnt: Counter = Counter()
        ans = left = 0
        n = len(nums)
        for right, x in enumerate(nums):
            cnt[x] += 1
            while len(cnt) == need:
                ans += n - right
                y = nums[left]
                cnt[y] -= 1
                if cnt[y] == 0:
                    del cnt[y]
                left += 1
        return ans

    def countCompleteSubarrays_brute(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate O(n^2) nested scan with a growing set.

        Algorithm:
        - For each start, add elements until set size equals global distinct count.

        Complexity: O(n^2) time, O(n) space.
        """
        total = len(set(nums))
        ans = 0
        n = len(nums)
        for i in range(n):
            s = set()
            for x in nums[i:]:
                s.add(x)
                if len(s) == total:
                    ans += 1
        return ans
# @lc code=end
