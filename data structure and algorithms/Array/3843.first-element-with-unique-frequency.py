#
# @lc app=leetcode id=3843 lang=python3
#
# [3843] First Element with Unique Frequency
#
# https://leetcode.com/problems/first-element-with-unique-frequency/description/
#
# algorithms
# Medium (70.34%)
# Likes:    84
# Dislikes: 6
# Total Accepted:    51.8K
# Total Submissions: 73.7K
# Testcase Example:  "[20,10,30,30]"
#
#
# You are given an integer array nums.
#
# Return an integer denoting the first element (scanning from left to
# right) in nums whose frequency is unique. That is, no other integer
# appears the same number of times in nums. If there is no such element,
# return -1.
#
# Example 1:
#
# Input: nums = [20,10,30,30]
#
# Output: 30
#
# Explanation:
#
# 20 appears once.
#
# 10 appears once.
#
# 30 appears twice.
#
# The frequency of 30 is unique because no other integer appears exactly
# twice.
#
# Example 2:
#
# Input: nums = [20,20,10,30,30,30]
#
# Output: 20
#
# Explanation:
#
# 20 appears twice.
#
# 10 appears once.
#
# 30 appears 3 times.
#
# The frequency of 20, 10, and 30 are unique. The first element that has
# unique frequency is 20.
#
# Example 3:
#
# Input: nums = [10,10,20,20]
#
# Output: -1
#
# Explanation:
#
# 10 appears twice.
#
# 20 appears twice.
#
# No element has a unique frequency.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start
from collections import Counter
from typing import List


class Solution:
    def firstUniqueFreq(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Find the leftmost value whose frequency is unique among all values.

        Algorithm:
        - Count value frequencies, then count how often each frequency occurs.
        - Scan left to right; return first value whose freq has global count 1.

        Complexity: O(n) time, O(n) space.
        """
        freq = Counter(nums)
        freq_count = Counter(freq.values())
        seen = set()
        for x in nums:
            if x in seen:
                continue
            seen.add(x)
            if freq_count[freq[x]] == 1:
                return x
        return -1
# @lc code=end
