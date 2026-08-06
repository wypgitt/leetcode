#
# @lc app=leetcode id=3940 lang=python3
#
# [3940] Limit Occurrences in Sorted Array
#
# https://leetcode.com/problems/limit-occurrences-in-sorted-array/description/
#
# algorithms
# Easy (73.41%)
# Likes:    36
# Dislikes: 0
# Total Accepted:    49.6K
# Total Submissions: 67.6K
# Testcase Example:  "[1,1,1,2,2,3]\n2"
#
#
# You are given a sorted integer array nums and an integer k.
#
# Return an array such that each distinct element appears at most k times,
# while preserving the relative order of the elements in nums.
#
# Note: If a distinct element appears at least k times, then it must
# appear exactly k times in the resulting array.
#
# Example 1:
#
# Input: nums = [1,1,1,2,2,3], k = 2
#
# Output: [1,1,2,2,3]
#
# Explanation:
#
# Each element can appear at most 2 times.
#
# The element 1 appears 3 times, so only 2 occurrences are kept.
#
# The element 2 appears 2 times, so both occurrences are kept.
#
# The element 3 appears 1 time, so it is kept.
#
# Thus, the resulting array is [1, 1, 2, 2, 3].
#
# Example 2:
#
# Input: nums = [1,2,3], k = 1
#
# Output: [1,2,3]
#
# Explanation:
#
# All elements are distinct and already appear at most once, so the array
# remains unchanged.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 1 <= nums[i] <= 100
#
# nums is sorted in non-decreasing order.
#
# 1 <= k <= nums.length
#
# Follow-up:
#
# Can you solve this in-place using O(1) extra space?
#
# Note that the space used for returning or resizing the result does not
# count toward the space complexity mentioned above, as some languages do
# not support in-place resizing.
#

# @lc code=start

class Solution:
    def limitOccurrences(self, nums: list[int], k: int) -> list[int]:
        """
        Interview explanation:
        Walk the sorted array and keep at most k copies of each distinct value.

        Algorithm:
        - Scan left to right; append while the run length for nums[i] is < k.

        Complexity: O(n) time, O(n) space for the answer.
        """
        ans = []
        for x in nums:
            if len(ans) < k or ans[-k] != x:
                ans.append(x)
        return ans

    def limitOccurrences_inplace(self, nums: list[int], k: int) -> list[int]:
        """
        Interview explanation:
        Alternate / follow-up: compact in-place with a write pointer.

        Algorithm:
        - w pointer; copy nums[i] when w < k or nums[w-k] != nums[i]; resize.

        Complexity: O(n) time, O(1) extra space.
        """
        w = 0
        for x in nums:
            if w < k or nums[w - k] != x:
                nums[w] = x
                w += 1
        return nums[:w]
# @lc code=end
