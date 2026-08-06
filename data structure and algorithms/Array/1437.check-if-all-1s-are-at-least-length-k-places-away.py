#
# @lc app=leetcode id=1437 lang=python3
#
# [1437] Check If All 1's Are at Least Length K Places Away
#
# https://leetcode.com/problems/check-if-all-1s-are-at-least-length-k-places-away/description/
#
# algorithms
# Easy (64.29%)
# Likes:    970
# Dislikes: 243
# Total Accepted:    218K
# Total Submissions: 340K
# Testcase Example:  "[1,0,0,0,1,0,0,1]"
#
# Given an binary array nums and an integer k, return true if all 1's are at
# least k places away from each other, otherwise return false.
#
# Example 1:
#
# Input: nums = [1,0,0,0,1,0,0,1], k = 2
# Output: true
# Explanation: Each of the 1s are at least 2 places away from each other.
#
# Example 2:
#
# Input: nums = [1,0,0,1,0,1], k = 2
# Output: false
# Explanation: The second 1 and third 1 are only one apart from each other.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 0 <= k <= nums.length
#
# nums[i] is 0 or 1
#

# @lc code=start
from typing import List


class Solution:
    def kLengthApart(self, nums: List[int], k: int) -> bool:
        """
        Interview explanation:
        All 1s must have at least k zeros between consecutive ones. Track last
        index of 1; ensure i-last-1 >= k.

        Algorithm:
        - prev=-inf; for i,x: if x==1: if i-prev-1<k: False; prev=i

        Complexity: O(n) time, O(1) space.
        """
        prev = -10**9
        for i, x in enumerate(nums):
            if x == 1:
                if i - prev - 1 < k:
                    return False
                prev = i
        return True

    def kLengthApart_twopointers(self, nums: List[int], k: int) -> bool:
        """
        Interview explanation:
        Alternate: collect indices of 1s; check consecutive differences.

        Algorithm:
        - idxs; all idxs[i]-idxs[i-1]-1 >= k

        Complexity: O(n) time, O(#ones) space.
        """
        idxs = [i for i, x in enumerate(nums) if x == 1]
        return all(idxs[i] - idxs[i - 1] - 1 >= k for i in range(1, len(idxs)))
# @lc code=end
