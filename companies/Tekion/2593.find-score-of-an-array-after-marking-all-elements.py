#
# @lc app=leetcode id=2593 lang=python3
#
# [2593] Find Score of an Array After Marking All Elements
#
# https://leetcode.com/problems/find-score-of-an-array-after-marking-all-elements/description/
#
# algorithms
# Medium (64.56%)
# Likes:    948
# Dislikes: 22
# Total Accepted:    137.5K
# Total Submissions: 213K
# Testcase Example:  "[2,1,3,4,5,2]"
#
# You are given an array nums consisting of positive integers.
#
# Starting with score = 0, apply the following algorithm:
#
#
# Choose the smallest integer of the array that is not marked. If there is a
# tie, choose the one with the smallest index.
#
#
# Add the value of the chosen integer to score.
#
#
# Mark the chosen element and its two adjacent elements if they exist.
#
#
# Repeat until all the array elements are marked.
#
# Return the score you get after applying the above algorithm.
#
#
#
# Example 1:
#
# Input: nums = [2,1,3,4,5,2]
# Output: 7
# Explanation: We mark the elements as follows:
# - 1 is the smallest unmarked element, so we mark it and its two adjacent
# elements: [2,1,3,4,5,2].
# - 2 is the smallest unmarked element, so we mark it and its left adjacent
# element: [2,1,3,4,5,2].
# - 4 is the only remaining unmarked element, so we mark it: [2,1,3,4,5,2].
# Our score is 1 + 2 + 4 = 7.
#
# Example 2:
#
# Input: nums = [2,3,5,1,3,2]
# Output: 5
# Explanation: We mark the elements as follows:
# - 1 is the smallest unmarked element, so we mark it and its two adjacent
# elements: [2,3,5,1,3,2].
# - 2 is the smallest unmarked element, since there are two of them, we choose
# the left-most one, so we mark the one at index 0 and its right adjacent
# element: [2,3,5,1,3,2].
# - 2 is the only remaining unmarked element, so we mark it: [2,3,5,1,3,2].
# Our score is 1 + 2 + 2 = 5.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 1 <= nums[i] <= 10^6
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def findScore(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Repeatedly choose smallest unmarked value (tie -> smallest index), add to score,
        and mark it and neighbors until all marked.

        Algorithm:
        - Min-heap of (value, index); skip already marked; mark i-1,i,i+1 on pick.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(nums)
        marked = [False] * n
        heap = [(v, i) for i, v in enumerate(nums)]
        heapq.heapify(heap)
        score = 0
        while heap:
            v, i = heapq.heappop(heap)
            if marked[i]:
                continue
            score += v
            for j in (i - 1, i, i + 1):
                if 0 <= j < n:
                    marked[j] = True
        return score
# @lc code=end
