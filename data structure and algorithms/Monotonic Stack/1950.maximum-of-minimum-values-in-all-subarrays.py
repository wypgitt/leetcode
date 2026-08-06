#
# @lc app=leetcode id=1950 lang=python3
#
# [1950] Maximum of Minimum Values in All Subarrays
#
# https://leetcode.com/problems/maximum-of-minimum-values-in-all-subarrays/description/
#
# algorithms
# Medium (48.22%)
# Likes:    147
# Dislikes: 56
# Total Accepted:    3.7K
# Total Submissions: 7.6K
# Testcase Example:  "[0,1,2,4]"
#
#
# You are given an integer array nums of size n. You are asked to solve n
# queries for each integer i in the range 0 <= i < n.
#
# To solve the i^th query:
#
# Find the minimum value in each possible subarray of size i + 1 of the
# array nums.
#
# Find the maximum of those minimum values. This maximum is the answer to
# the query.
#
# Return a 0-indexed integer array ans of size n such that ans[i] is the
# answer to the i^th query.
#
# A subarray is a contiguous sequence of elements in an array.
#
# Example 1:
#
# Input: nums = [0,1,2,4]
# Output: [4,2,1,0]
# Explanation:
# i=0:
# - The subarrays of size 1 are [0], [1], [2], [4]. The minimum values are
# 0, 1, 2, 4.
# - The maximum of the minimum values is 4.
# i=1:
# - The subarrays of size 2 are [0,1], [1,2], [2,4]. The minimum values
# are 0, 1, 2.
# - The maximum of the minimum values is 2.
# i=2:
# - The subarrays of size 3 are [0,1,2], [1,2,4]. The minimum values are
# 0, 1.
# - The maximum of the minimum values is 1.
# i=3:
# - There is one subarray of size 4, which is [0,1,2,4]. The minimum value
# is 0.
# - There is only one value, so the maximum is 0.
#
# Example 2:
#
# Input: nums = [10,20,50,10]
# Output: [50,20,10,10]
# Explanation:
# i=0:
# - The subarrays of size 1 are [10], [20], [50], [10]. The minimum values
# are 10, 20, 50, 10.
# - The maximum of the minimum values is 50.
# i=1:
# - The subarrays of size 2 are [10,20], [20,50], [50,10]. The minimum
# values are 10, 20, 10.
# - The maximum of the minimum values is 20.
# i=2:
# - The subarrays of size 3 are [10,20,50], [20,50,10]. The minimum values
# are 10, 10.
# - The maximum of the minimum values is 10.
# i=3:
# - There is one subarray of size 4, which is [10,20,50,10]. The minimum
# value is 10.
# - There is only one value, so the maximum is 10.
#
# Constraints:
#
# n == nums.length
#
# 1 <= n <= 10^5
#
# 0 <= nums[i] <= 10^9
#
# @lc code=start
from typing import List


class Solution:
    def findMaximums(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Premium. For each length k=1..n, answer[k-1] = max over all windows of
        length k of the minimum in that window. Equivalently: for each nums[i],
        find largest window where nums[i] is the minimum (via prev/next smaller);
        that value is a candidate for all lengths ≤ window size; take suffix max.

        Algorithm:
        - Mono stacks → left/right first strictly smaller. span = right-left-1.
          best[span] = max(best[span], nums[i]); then for i from n-1..1:
          best[i]=max(best[i], best[i+1]); return best[1..n].

        Complexity: O(n) time/space.
        """
        n = len(nums)
        left = [-1] * n
        right = [n] * n
        st = []
        for i, x in enumerate(nums):
            while st and nums[st[-1]] >= x:
                st.pop()
            left[i] = st[-1] if st else -1
            st.append(i)
        st = []
        for i in range(n - 1, -1, -1):
            while st and nums[st[-1]] >= nums[i]:
                st.pop()
            right[i] = st[-1] if st else n
            st.append(i)
        best = [0] * (n + 1)
        for i, x in enumerate(nums):
            span = right[i] - left[i] - 1
            best[span] = max(best[span], x)
        for k in range(n - 1, 0, -1):
            best[k] = max(best[k], best[k + 1])
        return best[1:]
# @lc code=end
