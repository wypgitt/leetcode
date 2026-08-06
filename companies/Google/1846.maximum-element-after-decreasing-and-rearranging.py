#
# @lc app=leetcode id=1846 lang=python3
#
# [1846] Maximum Element After Decreasing and Rearranging
#
# https://leetcode.com/problems/maximum-element-after-decreasing-and-rearranging/description/
#
# algorithms
# Medium (69.16%)
# Likes:    1347
# Dislikes: 291
# Total Accepted:    226K
# Total Submissions: 326K
# Testcase Example:  "[2,2,1,2,1]"
#
# You are given an array of positive integers arr. Perform some operations
# (possibly none) on arr so that it satisfies these conditions:
#
# The value of the first element in arr must be 1.
#
# The absolute difference between any 2 adjacent elements must be less than or
# equal to 1. In other words, abs(arr[i] - arr[i - 1]) <= 1 for each i where 1
# <= i < arr.length (0-indexed). abs(x) is the absolute value of x.
#
# There are 2 types of operations that you can perform any number of times:
#
# Decrease the value of any element of arr to a smaller positive integer.
#
# Rearrange the elements of arr to be in any order.
#
# Return the maximum possible value of an element in arr after performing the
# operations to satisfy the conditions.
#
# Example 1:
#
# Input: arr = [2,2,1,2,1]
# Output: 2
# Explanation:
# We can satisfy the conditions by rearranging arr so it becomes [1,2,2,2,1].
# The largest element in arr is 2.
#
# Example 2:
#
# Input: arr = [100,1,1000]
# Output: 3
# Explanation:
# One possible way to satisfy the conditions is by doing the following:
# 1. Rearrange arr so it becomes [1,100,1000].
# 2. Decrease the value of the second element to 2.
# 3. Decrease the value of the third element to 3.
# Now arr = [1,2,3], which satisfies the conditions.
# The largest element in arr is 3.
#
# Example 3:
#
# Input: arr = [1,2,3,4,5]
# Output: 5
# Explanation: The array already satisfies the conditions, and the largest
# element is 5.
#
# Constraints:
#
# 1 <= arr.length <= 10^5
#
# 1 <= arr[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def maximumElementAfterDecrementingAndRearranging(self, arr: List[int]) -> int:
        """
        Interview explanation:
        After rearrange/decrement with a[1]=1 and adjacent diff <=1, maximize max.
        Sort then greedily cap each next to prev+1.

        Algorithm (sort greedy):
        - Sort; prev=0; prev=min(x, prev+1) each; return prev.

        Complexity: O(n log n) time, O(1)/O(n) space.
        """
        arr.sort()
        prev = 0
        for x in arr:
            prev = min(x, prev + 1)
        return prev

    def maximumElementAfterDecrementingAndRearranging_count(self, arr: List[int]) -> int:
        """
        Interview explanation:
        Alternate O(n): cap values at n, count frequencies; the max achievable
        height grows by available counts but never exceeds the value index.

        Algorithm (counting):
        - freq[min(x,n)]++; ans=0; for v=1..n: ans=min(ans+freq[v], v).

        Complexity: O(n) time, O(n) space.
        """
        n = len(arr)
        freq = [0] * (n + 1)
        for x in arr:
            freq[min(x, n)] += 1
        ans = 0
        for v in range(1, n + 1):
            ans = min(ans + freq[v], v)
        return ans
# @lc code=end
