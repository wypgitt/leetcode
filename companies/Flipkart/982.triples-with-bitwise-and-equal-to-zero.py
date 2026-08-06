#
# @lc app=leetcode id=982 lang=python3
#
# [982] Triples with Bitwise AND Equal To Zero
#
# https://leetcode.com/problems/triples-with-bitwise-and-equal-to-zero/description/
#
# algorithms
# Hard (60.32%)
# Likes:    487
# Dislikes: 223
# Total Accepted:    25.8K
# Total Submissions: 42.8K
# Testcase Example:  "[2,1,3]"
#
# Given an integer array nums, return the number of AND triples.
#
# An AND triple is a triple of indices (i, j, k) such that:
#
# 0 <= i < nums.length
#
# 0 <= j < nums.length
#
# 0 <= k < nums.length
#
# nums[i] & nums[j] & nums[k] == 0, where & represents the bitwise-AND
# operator.
#
# Example 1:
#
# Input: nums = [2,1,3]
# Output: 12
# Explanation: We could choose the following i, j, k triples:
# (i=0, j=0, k=1) : 2 & 2 & 1
# (i=0, j=1, k=0) : 2 & 1 & 2
# (i=0, j=1, k=1) : 2 & 1 & 1
# (i=0, j=1, k=2) : 2 & 1 & 3
# (i=0, j=2, k=1) : 2 & 3 & 1
# (i=1, j=0, k=0) : 1 & 2 & 2
# (i=1, j=0, k=1) : 1 & 2 & 1
# (i=1, j=0, k=2) : 1 & 2 & 3
# (i=1, j=1, k=0) : 1 & 1 & 2
# (i=1, j=2, k=0) : 1 & 3 & 2
# (i=2, j=0, k=1) : 3 & 2 & 1
# (i=2, j=1, k=0) : 3 & 1 & 2
#
# Example 2:
#
# Input: nums = [0,0,0]
# Output: 27
#
# Constraints:
#
# 1 <= nums.length <= 1000
#
# 0 <= nums[i] < 2^16
#

# @lc code=start
from collections import Counter
from typing import List


class Solution:
    def countTriplets(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Precompute frequency of every pairwise AND (nums[i] & nums[j]). For
        each k, count pairs whose AND & nums[k] == 0. Values < 2^16 so the AND
        space is manageable.

        Algorithm:
        - cnt = Counter of a&b for all a,b in nums (n^2 pairs).
        - For each c in nums, for each (ab, freq) in cnt: if ab & c == 0:
          ans += freq.

        Complexity: O(n^2 + n * U) time where U = distinct pairwise ANDs
        (<= min(n^2, 2^16)), O(U) space.
        """
        cnt: Counter = Counter()
        for a in nums:
            for b in nums:
                cnt[a & b] += 1
        ans = 0
        for c in nums:
            for ab, freq in cnt.items():
                if ab & c == 0:
                    ans += freq
        return ans
# @lc code=end
