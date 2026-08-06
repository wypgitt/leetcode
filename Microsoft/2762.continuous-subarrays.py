#
# @lc app=leetcode id=2762 lang=python3
#
# [2762] Continuous Subarrays
#
# https://leetcode.com/problems/continuous-subarrays/description/
#
# algorithms
# Medium (58.00%)
# Likes:    1520
# Dislikes: 97
# Total Accepted:    122.1K
# Total Submissions: 210.5K
# Testcase Example:  "[5,4,2,4]"
#
# You are given a 0-indexed integer array nums. A subarray of nums is called
# continuous if:
#
#
# Let i, i + 1, ..., j_ be the indices in the subarray. Then, for each pair of
# indices i <= i_1, i_2 <= j, 0 <= |nums[i_1] - nums[i_2]| <= 2.
#
# Return the total number of continuous subarrays.
#
# A subarray is a contiguous non-empty sequence of elements within an array.
#
#
#
# Example 1:
#
# Input: nums = [5,4,2,4]
# Output: 8
# Explanation:
# Continuous subarray of size 1: [5], [4], [2], [4].
# Continuous subarray of size 2: [5,4], [4,2], [2,4].
# Continuous subarray of size 3: [4,2,4].
# There are no subarrys of size 4.
# Total continuous subarrays = 4 + 3 + 1 = 8.
# It can be shown that there are no more continuous subarrays.
#
#
#
# Example 2:
#
# Input: nums = [1,2,3]
# Output: 6
# Explanation:
# Continuous subarray of size 1: [1], [2], [3].
# Continuous subarray of size 2: [1,2], [2,3].
# Continuous subarray of size 3: [1,2,3].
# Total continuous subarrays = 3 + 2 + 1 = 6.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 1 <= nums[i] <= 10^9
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def continuousSubarrays(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Count subarrays where max - min <= 2.

        Algorithm:
        - Sliding window with two monotonic deques tracking max/min indices.
        - Shrink left while max - min > 2; add window length for each right.

        Complexity: O(n) time, O(n) space.
        """
        max_dq: deque[int] = deque()
        min_dq: deque[int] = deque()
        left = ans = 0
        for right, num in enumerate(nums):
            while max_dq and nums[max_dq[-1]] <= num:
                max_dq.pop()
            max_dq.append(right)
            while min_dq and nums[min_dq[-1]] >= num:
                min_dq.pop()
            min_dq.append(right)
            while nums[max_dq[0]] - nums[min_dq[0]] > 2:
                if max_dq[0] == left:
                    max_dq.popleft()
                if min_dq[0] == left:
                    min_dq.popleft()
                left += 1
            ans += right - left + 1
        return ans

    def continuousSubarrays_two_pointers(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: sliding window with a frequency map over values (range small).

        Algorithm:
        - Expand right; shrink left while max(freq keys) - min > 2 using Counter.

        Complexity: O(n) time (bounded distinct values in window), O(1) extra values.
        """
        from collections import Counter

        cnt: Counter = Counter()
        left = ans = 0
        for right, x in enumerate(nums):
            cnt[x] += 1
            while max(cnt) - min(cnt) > 2:
                y = nums[left]
                cnt[y] -= 1
                if cnt[y] == 0:
                    del cnt[y]
                left += 1
            ans += right - left + 1
        return ans
# @lc code=end
