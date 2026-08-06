#
# @lc app=leetcode id=220 lang=python3
#
# [220] Contains Duplicate III
#
# https://leetcode.com/problems/contains-duplicate-iii/description/
#
# algorithms
# Hard (25.04%)
# Likes:    1331
# Dislikes: 154
# Total Accepted:    328K
# Total Submissions: 1.3M
# Testcase Example:  "[1,2,3,1]"
#
# You are given an integer array nums and two integers indexDiff and valueDiff.
#
# Find a pair of indices (i, j) such that:
#
# i != j,
#
# abs(i - j) <= indexDiff.
#
# abs(nums[i] - nums[j]) <= valueDiff, and
#
# Return true if such pair exists or false otherwise.
#
# Example 1:
#
# Input: nums = [1,2,3,1], indexDiff = 3, valueDiff = 0
# Output: true
# Explanation: We can choose (i, j) = (0, 3).
# We satisfy the three conditions:
# i != j --> 0 != 3
# abs(i - j) <= indexDiff --> abs(0 - 3) <= 3
# abs(nums[i] - nums[j]) <= valueDiff --> abs(1 - 1) <= 0
#
# Example 2:
#
# Input: nums = [1,5,9,1,5,9], indexDiff = 2, valueDiff = 3
# Output: false
# Explanation: After trying all the possible pairs (i, j), we cannot satisfy
# the three conditions, so we return false.
#
# Constraints:
#
# 2 <= nums.length <= 10^5
#
# -10^9 <= nums[i] <= 10^9
#
# 1 <= indexDiff <= nums.length
#
# 0 <= valueDiff <= 10^9
#

# @lc code=start
from typing import Dict, List


class Solution:
    def containsNearbyAlmostDuplicate(self, nums: List[int], indexDiff: int, valueDiff: int) -> bool:
        """
        Interview explanation:
        Bucket numbers by size (valueDiff + 1). Two values within valueDiff land
        in the same or adjacent buckets. Keep only the last indexDiff indices'
        buckets — classic O(n) almost-duplicate check.

        Algorithm:
        - width = valueDiff + 1; map bucket_id -> value for the sliding window.
        - For nums[i], check buckets id-1, id, id+1 for a close value.
        - Insert current; erase nums[i - indexDiff] when window exceeds indexDiff.

        Complexity: O(n) time, O(min(n, indexDiff)) space.
        """
        if indexDiff <= 0 or valueDiff < 0:
            return False

        width = valueDiff + 1
        buckets: Dict[int, int] = {}

        def get_id(x: int) -> int:
            return x // width

        for i, x in enumerate(nums):
            bid = get_id(x)
            if bid in buckets:
                return True
            if bid - 1 in buckets and abs(x - buckets[bid - 1]) <= valueDiff:
                return True
            if bid + 1 in buckets and abs(x - buckets[bid + 1]) <= valueDiff:
                return True
            buckets[bid] = x
            if i >= indexDiff:
                del buckets[get_id(nums[i - indexDiff])]
        return False
# @lc code=end
