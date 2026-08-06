#
# @lc app=leetcode id=1793 lang=python3
#
# [1793] Maximum Score of a Good Subarray
#
# https://leetcode.com/problems/maximum-score-of-a-good-subarray/description/
#
# algorithms
# Hard (64.19%)
# Likes:    2028
# Dislikes: 50
# Total Accepted:    93.0K
# Total Submissions: 145K
# Testcase Example:  "[1,4,3,7,4,5]"
#
# You are given an array of integers nums (0-indexed) and an integer k.
#
# The score of a subarray (i, j) is defined as min(nums[i], nums[i+1], ...,
# nums[j]) * (j - i + 1). A good subarray is a subarray where i <= k <= j.
#
# Return the maximum possible score of a good subarray.
#
# Example 1:
#
# Input: nums = [1,4,3,7,4,5], k = 3
# Output: 15
# Explanation: The optimal subarray is (1, 5) with a score of min(4,3,7,4,5) *
# (5-1+1) = 3 * 5 = 15.
#
# Example 2:
#
# Input: nums = [5,5,4,5,4,1,1,1], k = 0
# Output: 20
# Explanation: The optimal subarray is (0, 4) with a score of min(5,5,4,5,4) *
# (4-0+1) = 4 * 5 = 20.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 2 * 10^4
#
# 0 <= k < nums.length
#

# @lc code=start
from typing import List


class Solution:
    def maximumScore(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Score of subarray [i,j] containing k is min(subarray)*length. Expand
        from k with two pointers: always extend toward the larger neighbor to
        keep the running min as large as possible; track max min*width.

        Algorithm:
        - i=j=k; cur_min=nums[k]; ans=nums[k]
        - While can expand: expand to the side with larger next value; update.

        Complexity: O(n) time, O(1) space.
        """
        n = len(nums)
        i = j = k
        cur_min = ans = nums[k]
        while i > 0 or j < n - 1:
            left = nums[i - 1] if i > 0 else -1
            right = nums[j + 1] if j < n - 1 else -1
            if left >= right:
                i -= 1
                cur_min = min(cur_min, nums[i])
            else:
                j += 1
                cur_min = min(cur_min, nums[j])
            ans = max(ans, cur_min * (j - i + 1))
        return ans

    def maximumScore_stack(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: for each index as the minimum, find largest subarray where
        it is the min (next smaller left/right via stack); if it covers k,
        candidate = nums[i]*(r-l-1).

        Algorithm:
        - Monotonic stack for prev/next strictly smaller; for each i with
          L < k < R: ans = max(ans, nums[i]*(R-L-1)).

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        left = [-1] * n
        right = [n] * n
        stack = []
        for i, x in enumerate(nums):
            while stack and nums[stack[-1]] > x:
                right[stack.pop()] = i
            stack.append(i)
        stack = []
        for i in range(n - 1, -1, -1):
            while stack and nums[stack[-1]] > nums[i]:
                left[stack.pop()] = i
            stack.append(i)
        ans = 0
        for i, x in enumerate(nums):
            if left[i] < k < right[i]:
                ans = max(ans, x * (right[i] - left[i] - 1))
        return ans
# @lc code=end
