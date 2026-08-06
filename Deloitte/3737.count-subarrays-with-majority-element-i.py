#
# @lc app=leetcode id=3737 lang=python3
#
# [3737] Count Subarrays With Majority Element I
#
# https://leetcode.com/problems/count-subarrays-with-majority-element-i/description/
#
# algorithms
# Medium (75.68%)
# Likes:    321
# Dislikes: 12
# Total Accepted:    137.1K
# Total Submissions: 181.2K
# Testcase Example:  "[1,2,2,3]\n2"
#
#
# You are given an integer array nums and an integer target.
#
# Return the number of subarrays of nums in which target is the majority
# element.
#
# The majority element of a subarray is the element that appears strictly
# more than half of the times in that subarray.
#
# Example 1:
#
# Input: nums = [1,2,2,3], target = 2
#
# Output: 5
#
# Explanation:
#
# Valid subarrays with target = 2 as the majority element:
#
# nums[1..1] = [2]
#
# nums[2..2] = [2]
#
# nums[1..2] = [2,2]
#
# nums[0..2] = [1,2,2]
#
# nums[1..3] = [2,2,3]
#
# So there are 5 such subarrays.
#
# Example 2:
#
# Input: nums = [1,1,1,1], target = 1
#
# Output: 10
#
# Explanation:
#
# ​​​​​​​All 10 subarrays have 1 as the majority element.
#
# Example 3:
#
# Input: nums = [1,2,3], target = 4
#
# Output: 0
#
# Explanation:
#
# target = 4 does not appear in nums at all. Therefore, there cannot be
# any subarray where 4 is the majority element. Hence the answer is 0.
#
# Constraints:
#
# 1 <= nums.length <= 1000
#
# 1 <= nums[i] <= 10^​​​​​​​9
#
# 1 <= target <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def countMajoritySubarrays(self, nums: List[int], target: int) -> int:
        """
        Interview explanation:
        n <= 1000, so count subarrays where target appears more than half by
        expanding each left endpoint.

        Algorithm:
        - For each start i, scan j while tracking target frequency; count when
          2 * freq > length.

        Complexity: O(n^2) time, O(1) space.
        """
        n = len(nums)
        ans = 0
        for i in range(n):
            freq = 0
            for j in range(i, n):
                freq += nums[j] == target
                if freq * 2 > j - i + 1:
                    ans += 1
        return ans

    def countMajoritySubarrays_bit(self, nums: List[int], target: int) -> int:
        """
        Interview explanation:
        Alternate: map target->+1 else -1; count subarrays with positive sum
        via Fenwick on prefix sums (same as the hard follow-up).

        Algorithm:
        - Offset prefixes into a BIT; query count of prior prefixes < current.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(nums)
        size = 2 * n + 1
        bit = [0] * (size + 1)

        def update(i: int, d: int) -> None:
            while i <= size:
                bit[i] += d
                i += i & -i

        def query(i: int) -> int:
            s = 0
            while i:
                s += bit[i]
                i -= i & -i
            return s

        s = n + 1
        update(s, 1)
        ans = 0
        for x in nums:
            s += 1 if x == target else -1
            ans += query(s - 1)
            update(s, 1)
        return ans
# @lc code=end

