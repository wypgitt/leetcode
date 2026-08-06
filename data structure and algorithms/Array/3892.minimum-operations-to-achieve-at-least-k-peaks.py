#
# @lc app=leetcode id=3892 lang=python3
#
# [3892] Minimum Operations to Achieve At Least K Peaks
#
# https://leetcode.com/problems/minimum-operations-to-achieve-at-least-k-peaks/description/
#
# algorithms
# Hard (30.78%)
# Likes:    47
# Dislikes: 7
# Total Accepted:    7.5K
# Total Submissions: 24.5K
# Testcase Example:  "[2,1,2]\n1"
#
#
# You are given a ​​​​​​​circular integer array​​​​​​​ nums of length n.
#
# An index i is a peak if its value is strictly greater than its
# neighbors:
#
# The previous neighbor of i is nums[i - 1] if i > 0, otherwise nums[n -
# 1].
#
# The next neighbor of i is nums[i + 1] if i < n - 1, otherwise nums[0].
#
# You are allowed to perform the following operation any number of times:
#
# Choose any index i and increase nums[i] by 1.
#
# Return an integer denoting the minimum number of operations required to
# make the array contain at least k peaks. If it is impossible, return -1.
#
# Example 1:
#
# Input: nums = [2,1,2], k = 1
#
# Output: 1
#
# Explanation:
#
# To achieve at least k = 1 peak, we can increase nums[2] = 2 to 3.
#
# After this operation, nums[2] = 3 is strictly greater than its neighbors
# nums[0] = 2 and nums[1] = 1.
#
# Therefore, the minimum number of operations required is 1.
#
# Example 2:
#
# Input: nums = [4,5,3,6], k = 2
#
# Output: 0
#
# Explanation:
#
# The array already contains at least k = 2 peaks with zero operations.
#
# Index 1: nums[1] = 5 is strictly greater than its neighbors nums[0] = 4
# and nums[2] = 3.
#
# Index 3: nums[3] = 6 is strictly greater than its neighbors nums[2] = 3
# and nums[0] = 4.
#
# Therefore, the minimum number of operations required is 0.
#
# Example 3:
#
# Input: nums = [3,7,3], k = 2
#
# Output: -1
#
# Explanation:
#
# It is impossible to have at least k = 2 peaks in this array. Therefore,
# the answer is -1.
#
# Constraints:
#
# 2 <= n == nums.length <= 5000
#
# -10^5 <= nums[i] <= 10^5
#
# 0 <= k <= n​​​​​​​
#

# @lc code=start
import heapq


class Solution:
    def minOperations(self, nums: list[int], k: int) -> int:
        """
        Interview explanation:
        Making index i a peak costs max(0, max(neighbors)+1 - nums[i]). Peaks
        cannot be adjacent on the circle → select k non-adjacent min-cost indices.

        Algorithm:
        - Classic circular non-adjacent k-selection via min-heap + linked list:
          repeatedly take cheapest index, delete neighbors, and merge with
          undo-cost cL+cR−c for possible later swaps.

        Complexity: O(n + k log n) time, O(n) space.
        """
        n = len(nums)
        if 2 * k > n:
            return -1
        if k == 0:
            return 0
        alive = [True] * n
        left = [(i - 1) % n for i in range(n)]
        right = [(i + 1) % n for i in range(n)]
        cost = [max(max(nums[left[i]], nums[right[i]]) + 1 - nums[i], 0) for i in range(n)]
        heap = [(cost[i], i) for i in range(n)]
        heapq.heapify(heap)
        result = 0
        taken = 0
        while heap and taken < k:
            c, i = heapq.heappop(heap)
            if not alive[i] or c != cost[i]:
                continue
            result += c
            taken += 1
            if taken == k:
                break
            # merge: replace neighbors with undo-capable super-node at i
            cost[i] = cost[left[i]] + cost[right[i]] - cost[i]
            heapq.heappush(heap, (cost[i], i))
            alive[left[i]] = alive[right[i]] = False
            left[i] = left[left[i]]
            right[i] = right[right[i]]
            right[left[i]] = left[right[i]] = i
        return result
# @lc code=end
