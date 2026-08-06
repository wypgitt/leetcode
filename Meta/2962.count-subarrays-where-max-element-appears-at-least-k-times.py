#
# @lc app=leetcode id=2962 lang=python3
#
# [2962] Count Subarrays Where Max Element Appears at Least K Times
#
# https://leetcode.com/problems/count-subarrays-where-max-element-appears-at-least-k-times/description/
#
# algorithms
# Medium (62.33%)
# Likes:    1734
# Dislikes: 82
# Total Accepted:    264.1K
# Total Submissions: 423.7K
# Testcase Example:  "[1,3,2,3,3]\n2"
#
#
# You are given an integer array nums and a positive integer k.
#
# Return the number of subarrays where the maximum element of nums appears
# at least k times in that subarray.
#
# A subarray is a contiguous sequence of elements within an array.
#
# Example 1:
#
# Input: nums = [1,3,2,3,3], k = 2
# Output: 6
# Explanation: The subarrays that contain the element 3 at least 2 times
# are: [1,3,2,3], [1,3,2,3,3], [3,2,3], [3,2,3,3], [2,3,3] and [3,3].
#
# Example 2:
#
# Input: nums = [1,4,2,1], k = 3
# Output: 0
# Explanation: No subarray contains the element 4 at least 3 times.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^6
#
# 1 <= k <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def countSubarrays(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Only the global maximum M matters: count subarrays where M appears >= k times.

        Algorithm:
        - Two pointers: expand right; track count of M. Shrink left while count >= k.
        - After shrink, every start in [0, left) yields a valid subarray ending at right
          (those starts still keep at least k copies of M).

        Complexity: O(n) time, O(1) space.
        """
        m = max(nums)
        ans = count = left = 0
        for right, x in enumerate(nums):
            if x == m:
                count += 1
            while count >= k:
                if nums[left] == m:
                    count -= 1
                left += 1
            ans += left
        return ans

    def countSubarrays_by_positions(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: use positions of the maximum; each window of k consecutive maxes
        defines a contiguous band of starts and ends.

        Algorithm:
        - Let idx be positions of max. For each window idx[t-k+1..t], starts are in
          (prev_max, idx[t-k+1]] and ends in [idx[t], n).

        Complexity: O(n) time, O(n) space.
        """
        m = max(nums)
        idx = [i for i, x in enumerate(nums) if x == m]
        if len(idx) < k:
            return 0
        n = len(nums)
        ans = 0
        for t in range(k - 1, len(idx)):
            prev = idx[t - k] if t - k >= 0 else -1
            ans += (idx[t - k + 1] - prev) * (n - idx[t])
        return ans
# @lc code=end
