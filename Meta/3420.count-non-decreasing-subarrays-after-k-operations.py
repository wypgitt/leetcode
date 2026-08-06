#
# @lc app=leetcode id=3420 lang=python3
#
# [3420] Count Non-Decreasing Subarrays After K Operations
#
# https://leetcode.com/problems/count-non-decreasing-subarrays-after-k-operations/description/
#
# algorithms
# Hard (25.19%)
# Likes:    88
# Dislikes: 4
# Total Accepted:    4.6K
# Total Submissions: 18.2K
# Testcase Example:  "[6,3,1,2,4,4]\n7"
#
#
# You are given an array nums of n integers and an integer k.
#
# For each subarray of nums, you can apply up to k operations on it. In
# each operation, you increment any element of the subarray by 1.
#
# Note that each subarray is considered independently, meaning changes
# made to one subarray do not persist to another.
#
# Return the number of subarrays that you can make non-decreasing
# ​​​​​after performing at most k operations.
#
# An array is said to be non-decreasing if each element is greater than or
# equal to its previous element, if it exists.
#
# Example 1:
#
# Input: nums = [6,3,1,2,4,4], k = 7
#
# Output: 17
#
# Explanation:
#
# Out of all 21 possible subarrays of nums, only the subarrays [6, 3, 1],
# [6, 3, 1, 2], [6, 3, 1, 2, 4] and [6, 3, 1, 2, 4, 4] cannot be made
# non-decreasing after applying up to k = 7 operations. Thus, the number
# of non-decreasing subarrays is 21 - 4 = 17.
#
# Example 2:
#
# Input: nums = [6,3,1,3,6], k = 4
#
# Output: 12
#
# Explanation:
#
# The subarray [3, 1, 3, 6] along with all subarrays of nums with three or
# fewer elements, except [6, 3, 1], can be made non-decreasing after k
# operations. There are 5 subarrays of a single element, 4 subarrays of
# two elements, and 2 subarrays of three elements except [6, 3, 1], so
# there are 1 + 5 + 4 + 2 = 12 subarrays that can be made non-decreasing.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# 1 <= k <= 10^9
#

# @lc code=start
from collections import deque
from typing import List, Tuple


class Solution:
    def countNonDecreasingSubarrays(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Count subarrays makeable non-decreasing with at most k increments.
        Cost of a window equals lifting each element up to the running
        max-from-the-left. Slide from right to left with a monotonic deque
        of (platform_value, count) after adjustments.

        Algorithm:
        - Expand left endpoint i right-to-left; merge smaller platforms into
          the new left value, adding cost.
        - Shrink right endpoint while cost > k.
        - All subarrays starting at i ending in [i..j] are valid.

        Complexity: O(n) time, O(n) space.
        """
        ans = 0
        cost = 0
        dq: deque[Tuple[int, int]] = deque()
        j = len(nums) - 1

        for i in range(len(nums) - 1, -1, -1):
            num = nums[i]
            count = 1
            while dq and dq[-1][0] < num:
                next_num, next_count = dq.pop()
                count += next_count
                cost += (num - next_num) * next_count
            dq.append((num, count))

            while cost > k:
                rightmost_num, rightmost_count = dq.popleft()
                cost -= rightmost_num - nums[j]
                j -= 1
                if rightmost_count > 1:
                    dq.appendleft((rightmost_num, rightmost_count - 1))

            ans += j - i + 1

        return ans
# @lc code=end
