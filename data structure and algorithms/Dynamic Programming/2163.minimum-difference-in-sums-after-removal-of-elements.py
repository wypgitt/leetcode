#
# @lc app=leetcode id=2163 lang=python3
#
# [2163] Minimum Difference in Sums After Removal of Elements
#
# https://leetcode.com/problems/minimum-difference-in-sums-after-removal-of-elements/description/
#
# algorithms
# Hard (69.60%)
# Likes:    1145
# Dislikes: 44
# Total Accepted:    84.6K
# Total Submissions: 121.6K
# Testcase Example:  "[3,1,2]"
#
# You are given a 0-indexed integer array nums consisting of 3 * n elements.
#
# You are allowed to remove any subsequence of elements of size exactly n from
# nums. The remaining 2 * n elements will be divided into two equal parts:
#
#
# The first n elements belonging to the first part and their sum is sum_first.
#
#
# The next n elements belonging to the second part and their sum is sum_second.
#
# The difference in sums of the two parts is denoted as sum_first - sum_second.
#
#
# For example, if sum_first = 3 and sum_second = 2, their difference is 1.
#
#
# Similarly, if sum_first = 2 and sum_second = 3, their difference is -1.
#
# Return the minimum difference possible between the sums of the two parts after
# the removal of n elements.
#
#
#
# Example 1:
#
# Input: nums = [3,1,2]
# Output: -1
# Explanation: Here, nums has 3 elements, so n = 1.
# Thus we have to remove 1 element from nums and divide the array into two equal
# parts.
# - If we remove nums[0] = 3, the array will be [1,2]. The difference in sums of
# the two parts will be 1 - 2 = -1.
# - If we remove nums[1] = 1, the array will be [3,2]. The difference in sums of
# the two parts will be 3 - 2 = 1.
# - If we remove nums[2] = 2, the array will be [3,1]. The difference in sums of
# the two parts will be 3 - 1 = 2.
# The minimum difference between sums of the two parts is min(-1,1,2) = -1.
#
# Example 2:
#
# Input: nums = [7,9,5,8,1,3]
# Output: 1
# Explanation: Here n = 2. So we must remove 2 elements and divide the remaining
# array into two parts containing two elements each.
# If we remove nums[2] = 5 and nums[3] = 8, the resultant array will be
# [7,9,1,3]. The difference in sums will be (7+9) - (1+3) = 12.
# To obtain the minimum difference, we should remove nums[1] = 9 and nums[4] =
# 1. The resultant array becomes [7,5,8,3]. The difference in sums of the two
# parts is (7+5) - (8+3) = 1.
# It can be shown that it is not possible to obtain a difference smaller than 1.
#
#
#
# Constraints:
#
#
# nums.length == 3 * n
#
#
# 1 <= n <= 10^5
#
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def minimumDifference(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Array of 3n elements. Remove n elements; among remaining 2n, first n
        form sum_first, last n form sum_second. Minimize sum_first - sum_second.

        Algorithm:
        (prefix min n-sum + suffix max n-sum)
        - left[i]: min sum of n elements chosen from nums[0..i] (i>=n-1), via
          max-heap of size n.
        - right[i]: max sum of n elements from nums[i..], via min-heap of size n.
        - Answer min over split i: left[i] - right[i+1] for valid i.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(nums) // 3
        N = len(nums)

        left = [0] * N
        max_h: List[int] = []
        s = 0
        for i in range(N):
            heapq.heappush(max_h, -nums[i])
            s += nums[i]
            if len(max_h) > n:
                s += heapq.heappop(max_h)  # remove largest (stored negative)
            if len(max_h) == n:
                left[i] = s

        right = [0] * (N + 1)
        min_h: List[int] = []
        s = 0
        for i in range(N - 1, -1, -1):
            heapq.heappush(min_h, nums[i])
            s += nums[i]
            if len(min_h) > n:
                s -= heapq.heappop(min_h)  # remove smallest
            if len(min_h) == n:
                right[i] = s

        ans = float("inf")
        for i in range(n - 1, 2 * n):
            ans = min(ans, left[i] - right[i + 1])
        return int(ans)
# @lc code=end
