#
# @lc app=leetcode id=3289 lang=python3
#
# [3289] The Two Sneaky Numbers of Digitville
#
# https://leetcode.com/problems/the-two-sneaky-numbers-of-digitville/description/
#
# algorithms
# Easy (89.81%)
# Likes:    542
# Dislikes: 22
# Total Accepted:    263.3K
# Total Submissions: 293.2K
# Testcase Example:  "[0,1,1,0]"
#
#
# In the town of Digitville, there was a list of numbers called nums
# containing integers from 0 to n - 1. Each number was supposed to appear
# exactly once in the list, however, two mischievous numbers sneaked in an
# additional time, making the list longer than usual.
#
# As the town detective, your task is to find these two sneaky numbers.
# Return an array of size two containing the two numbers (in any order),
# so peace can return to Digitville.
#
# Example 1:
#
# Input: nums = [0,1,1,0]
#
# Output: [0,1]
#
# Explanation:
#
# The numbers 0 and 1 each appear twice in the array.
#
# Example 2:
#
# Input: nums = [0,3,2,1,3,2]
#
# Output: [2,3]
#
# Explanation:
#
# The numbers 2 and 3 each appear twice in the array.
#
# Example 3:
#
# Input: nums = [7,1,5,4,3,4,6,0,9,5,8,2]
#
# Output: [4,5]
#
# Explanation:
#
# The numbers 4 and 5 each appear twice in the array.
#
# Constraints:
#
# 2 <= n <= 100
#
# nums.length == n + 2
#
# 0 <= nums[i] < n
#
# The input is generated such that nums contains exactly two repeated
# elements.
#

# @lc code=start
from typing import List


class Solution:
    def getSneakyNumbers(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Values 0..n-1 should appear once; exactly two values appear twice.

        Algorithm:
        - Track seen in a set; on second sighting, record the value.
        - Alternate: Counter / frequency array of size n.

        Complexity: O(n) time, O(n) space.
        """
        seen = set()
        ans = []
        for x in nums:
            if x in seen:
                ans.append(x)
            else:
                seen.add(x)
        return ans

    def getSneakyNumbers_freq(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Frequency array over 0..n-1.

        Algorithm:
        - Count occurrences; collect values with count == 2.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums) - 2
        freq = [0] * n
        for x in nums:
            freq[x] += 1
        return [i for i in range(n) if freq[i] == 2]
# @lc code=end
