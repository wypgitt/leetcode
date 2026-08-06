#
# @lc app=leetcode id=2537 lang=python3
#
# [2537] Count the Number of Good Subarrays
#
# https://leetcode.com/problems/count-the-number-of-good-subarrays/description/
#
# algorithms
# Medium (65.73%)
# Likes:    1589
# Dislikes: 60
# Total Accepted:    134.4K
# Total Submissions: 204.4K
# Testcase Example:  "[1,1,1,1,1]\n10"
#
# Given an integer array nums and an integer k, return the number of good
# subarrays of nums.
#
# A subarray arr is good if there are at least k pairs of indices (i, j) such
# that i < j and arr[i] == arr[j].
#
# A subarray is a contiguous non-empty sequence of elements within an array.
#
#
#
# Example 1:
#
# Input: nums = [1,1,1,1,1], k = 10
# Output: 1
# Explanation: The only good subarray is the array nums itself.
#
# Example 2:
#
# Input: nums = [3,1,4,3,2,2,4], k = 2
# Output: 4
# Explanation: There are 4 different good subarrays:
# - [3,1,4,3,2,2] that has 2 pairs.
# - [3,1,4,3,2,2,4] that has 3 pairs.
# - [1,4,3,2,2,4] that has 2 pairs.
# - [4,3,2,2,4] that has 2 pairs.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 1 <= nums[i], k <= 10^9
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def countGood(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Count subarrays with at least k equal-value pairs (i < j, equal elems).

        Algorithm:
        (Sliding window)
        - Expand right: adding x contributes cnt[x] new pairs.
        - Shrink left while window still has >= k pairs after removing left.
        - For each right, all starts in [0..left) form good subarrays ending at
          right (left is first index that makes window "minimal good" boundary);
          equivalently ans += left after shrinking to the shortest good window
          ending at right... use: while pairs >= k shrink, then ans += left.

        Complexity: O(n) time, O(n) space.
        """
        cnt: Counter[int] = Counter()
        ans = pairs = left = 0
        for x in nums:
            pairs += cnt[x]
            cnt[x] += 1
            while pairs >= k:
                cnt[nums[left]] -= 1
                pairs -= cnt[nums[left]]
                left += 1
            ans += left
        return ans

    def countGood_expand(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: for each left, expand right until pairs >= k, then add
        n - right good endings.

        Algorithm:
        - Two pointers; remove nums[left] when advancing left.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        cnt: Counter[int] = Counter()
        ans = pairs = 0
        right = -1
        for left in range(n):
            while pairs < k and right + 1 < n:
                right += 1
                pairs += cnt[nums[right]]
                cnt[nums[right]] += 1
            if pairs >= k:
                ans += n - right
            cnt[nums[left]] -= 1
            pairs -= cnt[nums[left]]
        return ans
# @lc code=end
