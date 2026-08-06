#
# @lc app=leetcode id=3634 lang=python3
#
# [3634] Minimum Removals to Balance Array
#
# https://leetcode.com/problems/minimum-removals-to-balance-array/description/
#
# algorithms
# Medium (47.84%)
# Likes:    621
# Dislikes: 28
# Total Accepted:    148.5K
# Total Submissions: 310.3K
# Testcase Example:  "[2,1,5]\n2"
#
#
# You are given an integer array nums and an integer k.
#
# An array is considered balanced if the value of its maximum element is
# at most k times the minimum element.
#
# You may remove any number of elements from nums​​​​​​​ without making it
# empty.
#
# Return the minimum number of elements to remove so that the remaining
# array is balanced.
#
# Note: An array of size 1 is considered balanced as its maximum and
# minimum are equal, and the condition always holds true.
#
# Example 1:
#
# Input: nums = [2,1,5], k = 2
#
# Output: 1
#
# Explanation:
#
# Remove nums[2] = 5 to get nums = [2, 1].
#
# Now max = 2, min = 1 and max <= min * k as 2 <= 1 * 2. Thus, the answer
# is 1.
#
# Example 2:
#
# Input: nums = [1,6,2,9], k = 3
#
# Output: 2
#
# Explanation:
#
# Remove nums[0] = 1 and nums[3] = 9 to get nums = [6, 2].
#
# Now max = 6, min = 2 and max <= min * k as 6 <= 2 * 3. Thus, the answer
# is 2.
#
# Example 3:
#
# Input: nums = [4,6], k = 2
#
# Output: 0
#
# Explanation:
#
# Since nums is already balanced as 6 <= 4 * 2, no elements need to be
# removed.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# 1 <= k <= 10^5
#

# @lc code=start

from typing import List


class Solution:
    def minRemoval(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        After removals, remaining values must satisfy max <= min*k. Sorting
        reduces this to finding the longest subarray (contiguous in sorted
        order) with nums[r] <= nums[l]*k; answer is n - that length.

        Algorithm:
        - Sort nums.
        - Two pointers: advance r, move l while nums[l]*k < nums[r]; track max
          window length.

        Complexity: O(n log n) time, O(1) extra space.
        """
        nums.sort()
        best = left = 0
        for right in range(len(nums)):
            while nums[left] * k < nums[right]:
                left += 1
            best = max(best, right - left + 1)
        return len(nums) - best
# @lc code=end

