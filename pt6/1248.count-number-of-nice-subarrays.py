#
# @lc app=leetcode id=1248 lang=python3
#
# [1248] Count Number of Nice Subarrays
#
# https://leetcode.com/problems/count-number-of-nice-subarrays/description/
#
# algorithms
# Medium (75.03%)
# Likes:    5456
# Dislikes: 150
# Total Accepted:    494K
# Total Submissions: 658.1K
# Testcase Example:  '[1,1,2,1,1]\n3'
#
# Given an array of integers nums and an integer k. A continuous subarray is
# called nice if there are k odd numbers on it.
# 
# Return the number of nice sub-arrays.
# 
# 
# Example 1:
# 
# 
# Input: nums = [1,1,2,1,1], k = 3
# Output: 2
# Explanation: The only sub-arrays with 3 odd numbers are [1,1,2,1] and
# [1,2,1,1].
# 
# 
# Example 2:
# 
# 
# Input: nums = [2,4,6], k = 1
# Output: 0
# Explanation: There are no odd numbers in the array.
# 
# 
# Example 3:
# 
# 
# Input: nums = [2,2,2,1,2,2,1,2,2,2], k = 2
# Output: 16
# 
# 
# 
# Constraints:
# 
# 
# 1 <= nums.length <= 50000
# 1 <= nums[i] <= 10^5
# 1 <= k <= nums.length
# 
# 
#

# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def numberOfSubarrays(self, nums: List[int], k: int) -> int:
        seen = defaultdict(int)
        seen[0] = 1
        odd_count = 0
        total = 0

        for num in nums:
            odd_count += num % 2
            total += seen[odd_count - k]
            seen[odd_count] += 1

        return total
# @lc code=end

# Explanation
# -----------
# Replace each number by whether it is odd and track the prefix count of odds.
# A subarray ending at the current index has exactly k odds if a previous
# prefix had odd_count - k odds. Count how many such prefixes have appeared.
#
# The hash map stores prefix-count frequencies. This is the same pattern as
# "subarray sum equals k", with odd counts as the prefix sum.
#
# Edge cases: consecutive even numbers create multiple prefixes with the same
# odd count; arrays with fewer than k odds naturally return 0; k = 1 works the
# same way.
#
# Time complexity: O(n).
# Space complexity: O(n) in the worst case for prefix counts.
