#
# @lc app=leetcode id=3159 lang=python3
#
# [3159] Find Occurrences of an Element in an Array
#
# https://leetcode.com/problems/find-occurrences-of-an-element-in-an-array/description/
#
# algorithms
# Medium (73.28%)
# Likes:    195
# Dislikes: 26
# Total Accepted:    63.1K
# Total Submissions: 86.1K
# Testcase Example:  "[1,3,1,7]\n[1,3,2,4]\n1"
#
#
# You are given an integer array nums, an integer array queries, and an
# integer x.
#
# For each queries[i], you need to find the index of the queries[i]^th
# occurrence of x in the nums array. If there are fewer than queries[i]
# occurrences of x, the answer should be -1 for that query.
#
# Return an integer array answer containing the answers to all queries.
#
# Example 1:
#
# Input: nums = [1,3,1,7], queries = [1,3,2,4], x = 1
#
# Output: [0,-1,2,-1]
#
# Explanation:
#
# For the 1^st query, the first occurrence of 1 is at index 0.
#
# For the 2^nd query, there are only two occurrences of 1 in nums, so the
# answer is -1.
#
# For the 3^rd query, the second occurrence of 1 is at index 2.
#
# For the 4^th query, there are only two occurrences of 1 in nums, so the
# answer is -1.
#
# Example 2:
#
# Input: nums = [1,2,3], queries = [10], x = 5
#
# Output: [-1]
#
# Explanation:
#
# For the 1^st query, 5 doesn't exist in nums, so the answer is -1.
#
# Constraints:
#
# 1 <= nums.length, queries.length <= 10^5
#
# 1 <= queries[i] <= 10^5
#
# 1 <= nums[i], x <= 10^4
#

# @lc code=start
from typing import List


class Solution:
    def occurrencesOfElement(
        self, nums: List[int], queries: List[int], x: int
    ) -> List[int]:
        """
        Interview explanation:
        For each query q, return the index of the q-th occurrence of x, or -1.

        Algorithm:
        - Collect indices where nums[i] == x.
        - Map query q to indices[q-1] when in range.

        Complexity: O(n + q) time, O(n) space.
        """
        idxs = [i for i, v in enumerate(nums) if v == x]
        return [idxs[q - 1] if q <= len(idxs) else -1 for q in queries]
# @lc code=end
