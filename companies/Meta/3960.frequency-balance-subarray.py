#
# @lc app=leetcode id=3960 lang=python3
#
# [3960] Frequency Balance Subarray
#
# https://leetcode.com/problems/frequency-balance-subarray/description/
#
# algorithms
# Medium (29.49%)
# Likes:    76
# Dislikes: 127
# Total Accepted:    21.9K
# Total Submissions: 74.4K
# Testcase Example:  "[1,2,2,1,2,3,3,3]"
#
#
# You are given an integer array ​​​​​​​nums.
#
# Define a frequency balance subarray as follows:
#
# If the subarray contains only one distinct value, it is frequency
# balanced.
#
# Otherwise, there must exist a positive integer f such that every
# distinct value in the subarray occurs either f or 2 * f times, and both
# frequencies occur among the distinct values.
#
# Return an integer denoting the length of the longest frequency balance
# subarray.
#
# Example 1:
#
# Input: nums = [1,2,2,1,2,3,3,3]
#
# Output: 5
#
# Explanation:
#
# The longest frequency balance subarray is [2, 1, 2, 3, 3].
#
# The elements that appear most frequently are 2 and 3, both appearing
# twice.
#
# The remaining element 1 appears once, meeting the requirements.
#
# Example 2:
#
# Input: nums = [5,5,5,5]
#
# Output: 4
#
# Explanation:
#
# The longest frequency balance subarray is [5, 5, 5, 5].
#
# The element that appears most frequently is 5.
#
# There are no other elements meeting the requirements.
#
# Example 3:
#
# Input: nums = [1,2,3,4]
#
# Output: 1
#
# Explanation:
#
# Since all elements appear only once, the length of the longest frequency
# balance subarray is 1.
#
# Constraints:
#
# 1 <= nums.length <= 10^​​​​​​​3
#
# 1 <= nums[i] <= 10^​​​​​​​9
#

# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def getLength(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Longest subarray that is either unary, or whose frequencies are only
        {f, 2f} with both present.

        Algorithm:
        - Enumerate left endpoints; expand right while maintaining value→freq
          and freq→count maps.
        - Update answer when |cnt|==1 or (|freq|==2 and one key doubles the other).

        Complexity: O(n²) time, O(n) space.
        """
        n = len(nums)
        ans = 1
        for left in range(n):
            cnt = defaultdict(int)
            freq = defaultdict(int)
            for right in range(left, n):
                x = nums[right]
                old = cnt[x]
                if old:
                    freq[old] -= 1
                    if freq[old] == 0:
                        del freq[old]
                cnt[x] = old + 1
                freq[old + 1] += 1
                if len(cnt) == 1:
                    ans = max(ans, right - left + 1)
                elif len(freq) == 2:
                    a, b = sorted(freq.keys())
                    if b == 2 * a:
                        ans = max(ans, right - left + 1)
        return ans
# @lc code=end
