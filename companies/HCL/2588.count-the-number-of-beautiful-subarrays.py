#
# @lc app=leetcode id=2588 lang=python3
#
# [2588] Count the Number of Beautiful Subarrays
#
# https://leetcode.com/problems/count-the-number-of-beautiful-subarrays/description/
#
# algorithms
# Medium (54.51%)
# Likes:    571
# Dislikes: 24
# Total Accepted:    28.7K
# Total Submissions: 52.6K
# Testcase Example:  "[4,3,1,2,4]"
#
# You are given a 0-indexed integer array nums. In one operation, you can:
#
#
# Choose two different indices i and j such that 0 <= i, j < nums.length.
#
#
# Choose a non-negative integer k such that the k^th bit (0-indexed) in the
# binary representation of nums[i] and nums[j] is 1.
#
#
# Subtract 2^k from nums[i] and nums[j].
#
# A subarray is beautiful if it is possible to make all of its elements equal to
# 0 after applying the above operation any number of times (including zero).
#
# Return the number of beautiful subarrays in the array nums.
#
# A subarray is a contiguous non-empty sequence of elements within an array.
#
# Note: Subarrays where all elements are initially 0 are considered beautiful,
# as no operation is needed.
#
#
#
# Example 1:
#
# Input: nums = [4,3,1,2,4]
# Output: 2
# Explanation: There are 2 beautiful subarrays in nums: [4,3,1,2,4] and
# [4,3,1,2,4].
# - We can make all elements in the subarray [3,1,2] equal to 0 in the following
# way:
#   - Choose [3, 1, 2] and k = 1. Subtract 2^1 from both numbers. The subarray
# becomes [1, 1, 0].
#   - Choose [1, 1, 0] and k = 0. Subtract 2^0 from both numbers. The subarray
# becomes [0, 0, 0].
# - We can make all elements in the subarray [4,3,1,2,4] equal to 0 in the
# following way:
#   - Choose [4, 3, 1, 2, 4] and k = 2. Subtract 2^2 from both numbers. The
# subarray becomes [0, 3, 1, 2, 0].
#   - Choose [0, 3, 1, 2, 0] and k = 0. Subtract 2^0 from both numbers. The
# subarray becomes [0, 2, 0, 2, 0].
#   - Choose [0, 2, 0, 2, 0] and k = 1. Subtract 2^1 from both numbers. The
# subarray becomes [0, 0, 0, 0, 0].
#
# Example 2:
#
# Input: nums = [1,10,4]
# Output: 0
# Explanation: There are no beautiful subarrays in nums.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 0 <= nums[i] <= 10^6
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def beautifulSubarrays(self, nums: List[int]) -> int:
        """
        Interview explanation:
        A subarray is beautiful if its XOR is 0 (each bit appears even times / can be
        reduced to empty by subtracting equal pairs of powers of two).

        Algorithm:
        - Prefix XOR + hashmap of frequencies; for each prefix add count of same XOR.

        Complexity: O(n) time, O(n) space.
        """
        pref = 0
        cnt = Counter({0: 1})
        ans = 0
        for x in nums:
            pref ^= x
            ans += cnt[pref]
            cnt[pref] += 1
        return ans
# @lc code=end
