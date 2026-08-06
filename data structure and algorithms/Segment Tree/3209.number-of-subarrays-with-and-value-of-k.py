#
# @lc app=leetcode id=3209 lang=python3
#
# [3209] Number of Subarrays With AND Value of K
#
# https://leetcode.com/problems/number-of-subarrays-with-and-value-of-k/description/
#
# algorithms
# Hard (35.80%)
# Likes:    174
# Dislikes: 8
# Total Accepted:    14.5K
# Total Submissions: 40.5K
# Testcase Example:  "[1,1,1]\n1"
#
#
# Given an array of integers nums and an integer k, return the number of
# subarrays of nums where the bitwise AND of the elements of the subarray
# equals k.
#
# Example 1:
#
# Input: nums = [1,1,1], k = 1
#
# Output: 6
#
# Explanation:
#
# All subarrays contain only 1's.
#
# Example 2:
#
# Input: nums = [1,1,2], k = 1
#
# Output: 3
#
# Explanation:
#
# Subarrays having an AND value of 1 are: [1,1,2], [1,1,2], [1,1,2].
#
# Example 3:
#
# Input: nums = [1,2,3], k = 2
#
# Output: 2
#
# Explanation:
#
# Subarrays having an AND value of 2 are: [1,2,3], [1,2,3].
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 0 <= nums[i], k <= 10^9
#

# @lc code=start
from typing import Dict, List


class Solution:
    def countSubarrays(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Count subarrays whose bitwise AND equals k. AND only clears bits, and
        the number of distinct AND values of subarrays ending at a fixed index
        is O(bit-width) (~30).

        Algorithm:
        - Maintain a map: AND-value → count of subarrays ending at the previous
          index.
        - For each num, form new map by ANDing num into each previous value
          (and the singleton [num]); add the count of key k to the answer.
        - Optional prune: if (num & k) != k, no subarray ending here can equal k.

        Complexity: O(n * log A) time, O(log A) space (A = value range).
        """
        ans = 0
        prev: Dict[int, int] = {}
        for num in nums:
            cur: Dict[int, int] = {num: 1}
            for val, cnt in prev.items():
                new_val = val & num
                cur[new_val] = cur.get(new_val, 0) + cnt
            ans += cur.get(k, 0)
            prev = cur
        return ans
# @lc code=end
