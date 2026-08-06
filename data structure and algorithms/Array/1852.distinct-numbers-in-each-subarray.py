#
# @lc app=leetcode id=1852 lang=python3
#
# [1852] Distinct Numbers in Each Subarray
#
# https://leetcode.com/problems/distinct-numbers-in-each-subarray/description/
#
# algorithms
# Medium (77.40%)
# Likes:    157
# Dislikes: 10
# Total Accepted:    17.1K
# Total Submissions: 22.1K
# Testcase Example:  "[1,2,3,2,2,1,3]\n3"
#
#
# You are given an integer array nums of length n and an integer k. Your
# task is to find the number of distinct elements in every subarray of
# size k within nums.
#
# Return an array ans such that ans[i] is the count of distinct elements
# in nums[i..(i + k - 1)] for each index 0 <= i < n - k.
#
# Example 1:
#
# Input: nums = [1,2,3,2,2,1,3], k = 3
# Output: [3,2,2,2,3]
# Explanation: The number of distinct elements in each subarray goes as
# follows:
# - nums[0..2] = [1,2,3] so ans[0] = 3
# - nums[1..3] = [2,3,2] so ans[1] = 2
# - nums[2..4] = [3,2,2] so ans[2] = 2
# - nums[3..5] = [2,2,1] so ans[3] = 2
# - nums[4..6] = [2,1,3] so ans[4] = 3
#
# Example 2:
#
# Input: nums = [1,1,1,1,2,3,4], k = 4
# Output: [1,2,3,4]
# Explanation: The number of distinct elements in each subarray goes as
# follows:
# - nums[0..3] = [1,1,1,1] so ans[0] = 1
# - nums[1..4] = [1,1,1,2] so ans[1] = 2
# - nums[2..5] = [1,1,2,3] so ans[2] = 3
# - nums[3..6] = [1,2,3,4] so ans[3] = 4
#
# Constraints:
#
# 1 <= k <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#
# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def distinctNumbers(self, nums: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        Premium: return distinct count in every contiguous subarray of size k.
        Sliding window with frequency map; distinct = number of keys with
        positive count.

        Algorithm (sliding window + Counter):
        - Build freq for first k elements; append len(freq).
        - Slide: add nums[i], remove nums[i-k] (pop if zero); append len(freq).

        Complexity: O(n) time, O(k) space.
        """
        n = len(nums)
        freq = Counter(nums[:k])
        ans = [len(freq)]
        for i in range(k, n):
            freq[nums[i]] += 1
            left = nums[i - k]
            freq[left] -= 1
            if freq[left] == 0:
                del freq[left]
            ans.append(len(freq))
        return ans

    def distinctNumbers_set_per_window(self, nums: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        Alternate: rebuild a set for each window (simpler, slower).

        Algorithm:
        - For i in 0..n-k: ans.append(len(set(nums[i:i+k]))).

        Complexity: O(n*k) time.
        """
        return [len(set(nums[i : i + k])) for i in range(len(nums) - k + 1)]
# @lc code=end
