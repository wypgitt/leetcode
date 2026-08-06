#
# @lc app=leetcode id=239 lang=python3
#
# [239] Sliding Window Maximum
#
# https://leetcode.com/problems/sliding-window-maximum/description/
#
# algorithms
# Hard (49.07%)
# Likes:    20747
# Dislikes: 853
# Total Accepted:    1.8M
# Total Submissions: 3.6M
# Testcase Example:  "[1,3,-1,-3,5,3,6,7]"
#
# You are given an array of integers nums, there is a sliding window of size k
# which is moving from the very left of the array to the very right. You can
# only see the k numbers in the window. Each time the sliding window moves
# right by one position.
#
# Return the max sliding window.
#
# Example 1:
#
# Input: nums = [1,3,-1,-3,5,3,6,7], k = 3
# Output: [3,3,5,5,6,7]
# Explanation:
# Window position Max
# --------------- -----
# [1 3 -1] -3 5 3 6 7 3
# 1 [3 -1 -3] 5 3 6 7 3
# 1 3 [-1 -3 5] 3 6 7 5
# 1 3 -1 [-3 5 3] 6 7 5
# 1 3 -1 -3 [5 3 6] 7 6
# 1 3 -1 -3 5 [3 6 7] 7
#
# Example 2:
#
# Input: nums = [1], k = 1
# Output: [1]
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -10^4 <= nums[i] <= 10^4
#
# 1 <= k <= nums.length
#

# @lc code=start
from collections import deque
from typing import Deque, List


class Solution:
    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        Monotonic decreasing deque of indices: front is always the window max.
        Drop indices outside the window and smaller values from the back before
        pushing the current index.

        Algorithm:
        - For each i: pop left if index <= i-k; pop right while nums[dq[-1]] < nums[i].
        - Append i; if i >= k-1, record nums[dq[0]].

        Complexity: O(n) time, O(k) space.
        """
        dq: Deque[int] = deque()
        ans: List[int] = []
        for i, x in enumerate(nums):
            while dq and dq[0] <= i - k:
                dq.popleft()
            while dq and nums[dq[-1]] < x:
                dq.pop()
            dq.append(i)
            if i >= k - 1:
                ans.append(nums[dq[0]])
        return ans
# @lc code=end
