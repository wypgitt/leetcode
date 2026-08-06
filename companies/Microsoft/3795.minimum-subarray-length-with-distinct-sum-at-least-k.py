#
# @lc app=leetcode id=3795 lang=python3
#
# [3795] Minimum Subarray Length With Distinct Sum At Least K
#
# https://leetcode.com/problems/minimum-subarray-length-with-distinct-sum-at-least-k/description/
#
# algorithms
# Medium (31.99%)
# Likes:    89
# Dislikes: 11
# Total Accepted:    31.4K
# Total Submissions: 98.2K
# Testcase Example:  "[2,2,3,1]\n4"
#
#
# You are given an integer array nums and an integer k.
#
# Return the minimum length of a subarray whose sum of the distinct values
# present in that subarray (each value counted once) is at least k. If no
# such subarray exists, return -1.
#
# Example 1:
#
# Input: nums = [2,2,3,1], k = 4
#
# Output: 2
#
# Explanation:
#
# The subarray [2, 3] has distinct elements {2, 3} whose sum is 2 + 3 = 5,
# which is ​​​​​​​at least k = 4. Thus, the answer is 2.
#
# Example 2:
#
# Input: nums = [3,2,3,4], k = 5
#
# Output: 2
#
# Explanation:
#
# The subarray [3, 2] has distinct elements {3, 2} whose sum is 3 + 2 = 5,
# which is ​​​​​​​at least k = 5. Thus, the answer is 2.
#
# Example 3:
#
# Input: nums = [5,5,4], k = 5
#
# Output: 1
#
# Explanation:
#
# The subarray [5] has distinct elements {5} whose sum is 5, which is at
# least k = 5. Thus, the answer is 1.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#
# 1 <= k <= 10^9
#

# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def minLength(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Minimize window length whose sum of distinct values is >= k. Expand right,
        shrink left while the distinct-sum stays >= k.

        Algorithm:
        - freq map + running distinct sum s.
        - On first occurrence of x, s += x; while s >= k, update ans and pop left.
        - Return ans or -1.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        cnt: dict[int, int] = defaultdict(int)
        ans = n + 1
        s = l = 0
        for r, x in enumerate(nums):
            cnt[x] += 1
            if cnt[x] == 1:
                s += x
            while s >= k:
                ans = min(ans, r - l + 1)
                y = nums[l]
                cnt[y] -= 1
                if cnt[y] == 0:
                    s -= y
                l += 1
        return -1 if ans > n else ans
# @lc code=end
