#
# @lc app=leetcode id=3347 lang=python3
#
# [3347] Maximum Frequency of an Element After Performing Operations II
#
# https://leetcode.com/problems/maximum-frequency-of-an-element-after-performing-operations-ii/description/
#
# algorithms
# Hard (53.74%)
# Likes:    319
# Dislikes: 21
# Total Accepted:    68.4K
# Total Submissions: 127.3K
# Testcase Example:  "[1,4,5]\n1\n2"
#
#
# You are given an integer array nums and two integers k and
# numOperations.
#
# You must perform an operation numOperations times on nums, where in each
# operation you:
#
# Select an index i that was not selected in any previous operations.
#
# Add an integer in the range [-k, k] to nums[i].
#
# Return the maximum possible frequency of any element in nums after
# performing the operations.
#
# Example 1:
#
# Input: nums = [1,4,5], k = 1, numOperations = 2
#
# Output: 2
#
# Explanation:
#
# We can achieve a maximum frequency of two by:
#
# Adding 0 to nums[1], after which nums becomes [1, 4, 5].
#
# Adding -1 to nums[2], after which nums becomes [1, 4, 4].
#
# Example 2:
#
# Input: nums = [5,11,20,20], k = 5, numOperations = 1
#
# Output: 2
#
# Explanation:
#
# We can achieve a maximum frequency of two by:
#
# Adding 0 to nums[1].
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# 0 <= k <= 10^9
#
# 0 <= numOperations <= nums.length
#

# @lc code=start

from typing import List
from collections import Counter
import bisect


class Solution:
    def maxFrequency(self, nums: List[int], k: int, numOperations: int) -> int:
        """
        Interview explanation:
        Same as I but values up to 1e9. Only O(n) candidate targets matter:
        each nums[i] and nums[i]±k. Sort + binary search the reachable window.

        Algorithm:
        - Sort nums; Counter for exact frequencies.
        - For each candidate T, count nums in [T-k, T+k]; answer
          min(that, freq[T] + numOperations).

        Complexity: O(n log n) time, O(n) space.
        """
        nums.sort()
        cnt = Counter(nums)
        cands = set()
        for x in nums:
            cands.add(x)
            cands.add(x - k)
            cands.add(x + k)
        ans = 0
        for t in cands:
            L = bisect.bisect_left(nums, t - k)
            R = bisect.bisect_right(nums, t + k)
            ans = max(ans, min(R - L, cnt.get(t, 0) + numOperations))
        return ans
# @lc code=end
