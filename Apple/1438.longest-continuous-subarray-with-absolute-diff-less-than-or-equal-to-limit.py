#
# @lc app=leetcode id=1438 lang=python3
#
# [1438] Longest Continuous Subarray With Absolute Diff Less Than or Equal to Limit
#
# https://leetcode.com/problems/longest-continuous-subarray-with-absolute-diff-less-than-or-equal-to-limit/description/
#
# algorithms
# Medium (57.89%)
# Likes:    4573
# Dislikes: 231
# Total Accepted:    327K
# Total Submissions: 564K
# Testcase Example:  "[8,2,4,7]"
#
# Given an array of integers nums and an integer limit, return the size of the
# longest non-empty subarray such that the absolute difference between any two
# elements of this subarray is less than or equal to limit.
#
# Example 1:
#
# Input: nums = [8,2,4,7], limit = 4
# Output: 2
# Explanation: All subarrays are:
# [8] with maximum absolute diff |8-8| = 0 <= 4.
# [8,2] with maximum absolute diff |8-2| = 6 > 4.
# [8,2,4] with maximum absolute diff |8-2| = 6 > 4.
# [8,2,4,7] with maximum absolute diff |8-2| = 6 > 4.
# [2] with maximum absolute diff |2-2| = 0 <= 4.
# [2,4] with maximum absolute diff |2-4| = 2 <= 4.
# [2,4,7] with maximum absolute diff |2-7| = 5 > 4.
# [4] with maximum absolute diff |4-4| = 0 <= 4.
# [4,7] with maximum absolute diff |4-7| = 3 <= 4.
# [7] with maximum absolute diff |7-7| = 0 <= 4.
# Therefore, the size of the longest subarray is 2.
#
# Example 2:
#
# Input: nums = [10,1,2,4,7,2], limit = 5
# Output: 4
# Explanation: The subarray [2,4,7,2] is the longest since the maximum absolute
# diff is |2-7| = 5 <= 5.
#
# Example 3:
#
# Input: nums = [4,2,2,2,4,4,2,2], limit = 0
# Output: 3
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# 0 <= limit <= 10^9
#

# @lc code=start
from typing import List
from collections import deque
import heapq


class Solution:
    def longestSubarray(self, nums: List[int], limit: int) -> int:
        """
        Interview explanation:
        Longest subarray with max-min <= limit. Sliding window + two mono deques
        for window max/min; shrink left while max-min > limit.

        Algorithm:
        (two deques)
        - maxd decreasing, mind increasing of indices; expand r; shrink l; track best.

        Complexity: O(n) time, O(n) space.
        """
        maxd, mind = deque(), deque()
        l = 0
        ans = 0
        for r, x in enumerate(nums):
            while maxd and nums[maxd[-1]] < x:
                maxd.pop()
            while mind and nums[mind[-1]] > x:
                mind.pop()
            maxd.append(r)
            mind.append(r)
            while nums[maxd[0]] - nums[mind[0]] > limit:
                l += 1
                if maxd[0] < l:
                    maxd.popleft()
                if mind[0] < l:
                    mind.popleft()
            ans = max(ans, r - l + 1)
        return ans

    def longestSubarray_heap(self, nums: List[int], limit: int) -> int:
        """
        Interview explanation:
        Alternate: lazy heaps for window max/min with left index validity.

        Algorithm:
        - maxh/minh of (-val,i)/(val,i); shrink while max-min>limit.

        Complexity: O(n log n) time, O(n) space.
        """
        maxh, minh = [], []
        l = ans = 0
        for r, x in enumerate(nums):
            heapq.heappush(maxh, (-x, r))
            heapq.heappush(minh, (x, r))
            while -maxh[0][0] - minh[0][0] > limit:
                l += 1
                while maxh and maxh[0][1] < l:
                    heapq.heappop(maxh)
                while minh and minh[0][1] < l:
                    heapq.heappop(minh)
            ans = max(ans, r - l + 1)
        return ans
# @lc code=end
