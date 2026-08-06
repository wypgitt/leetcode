#
# @lc app=leetcode id=169 lang=python3
#
# [169] Majority Element
#
# https://leetcode.com/problems/majority-element/description/
#
# algorithms
# Easy (66.46%)
# Likes:    23083
# Dislikes: 835
# Total Accepted:    5.8M
# Total Submissions: 8.8M
# Testcase Example:  "[3,2,3]"
#
# Given an array nums of size n, return the majority element.
#
# The majority element is the element that appears more than ⌊n / 2⌋ times. You
# may assume that the majority element always exists in the array.
#
# Example 1:
#
# Input: nums = [3,2,3]
# Output: 3
#
# Example 2:
#
# Input: nums = [2,2,1,1,1,2,2]
# Output: 2
#
# Constraints:
#
# n == nums.length
#
# 1 <= n <= 5 * 10^4
#
# -10^9 <= nums[i] <= 10^9
#
# The input is generated such that a majority element will exist in the array.
#
# Follow-up: Could you solve the problem in linear time and in O(1) space?
#

# @lc code=start
from collections import Counter
from typing import List


class Solution:
    def majorityElement(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Boyer-Moore voting: majority (> n/2) survives pairwise cancellation of
        different values, so the final candidate is the majority.

        Algorithm:
        - Maintain candidate and count.
        - Same as candidate -> count++; else count--; if count hits 0, adopt
          current value as candidate with count 1.
        - Return candidate (guaranteed to exist).

        Complexity: O(n) time, O(1) space.
        """
        candidate = None
        count = 0
        for num in nums:
            if count == 0:
                candidate = num
            count += 1 if num == candidate else -1
        return candidate

    def majorityElement_hash(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: count frequencies with a hash map and return the key with
        count > n // 2.

        Algorithm:
        - Counter(nums); return the element whose frequency exceeds n // 2.

        Complexity: O(n) time, O(n) space.
        """
        counts = Counter(nums)
        threshold = len(nums) // 2
        for num, freq in counts.items():
            if freq > threshold:
                return num
        raise ValueError("no majority element")
# @lc code=end
