#
# @lc app=leetcode id=398 lang=python3
#
# [398] Random Pick Index
#
# https://leetcode.com/problems/random-pick-index/description/
#
# algorithms
# Medium (65.11%)
# Likes:    1403
# Dislikes: 1309
# Total Accepted:    312K
# Total Submissions: 479K
# Testcase Example:  "[\"Solution\",\"pick\",\"pick\",\"pick\"]"
#
# Given an integer array nums with possible duplicates, randomly output the
# index of a given target number. You can assume that the given target number
# must exist in the array.
#
# Implement the Solution class:
#
# Solution(int[] nums) Initializes the object with the array nums.
#
# int pick(int target) Picks a random index i from nums where nums[i] ==
# target. If there are multiple valid i's, then each index should have an equal
# probability of returning.
#
# Example 1:
#
# Input
# ["Solution", "pick", "pick", "pick"]
# [[[1, 2, 3, 3, 3]], [3], [1], [3]]
# Output
# [null, 4, 0, 2]
#
# Explanation
# Solution solution = new Solution([1, 2, 3, 3, 3]);
# solution.pick(3); // It should return either index 2, 3, or 4 randomly. Each
# index should have equal probability of returning.
# solution.pick(1); // It should return 0. Since in the array only nums[0] is
# equal to 1.
# solution.pick(3); // It should return either index 2, 3, or 4 randomly. Each
# index should have equal probability of returning.
#
# Constraints:
#
# 1 <= nums.length <= 2 * 10^4
#
# -2^31 <= nums[i] <= 2^31 - 1
#
# target is an integer from nums.
#
# At most 10^4 calls will be made to pick.
#

# @lc code=start
import random
from typing import List


class Solution:
    """
    Interview explanation:
    Reservoir sampling over indices matching target: on the c-th occurrence,
    replace chosen index with probability 1/c. Uniform among all matches;
    O(1) extra space if nums is huge (vs hashing all indices).

    Algorithm:
    - __init__: store nums.
    - pick: walk nums; when nums[i]==target, count++; with prob 1/count keep i.

    Complexity: pick O(n) time, O(1) extra space.
    """

    def __init__(self, nums: List[int]):
        """
        Interview explanation:
        Store the array; pick uses reservoir sampling so we need no index map
        (useful when nums is huge / read-only).

        Algorithm:
        - Keep a reference to nums.

        Complexity: O(1) time, O(1) extra space beyond the input.
        """
        self.nums = nums

    def pick(self, target: int) -> int:
        """
        Interview explanation:
        Reservoir sampling over matching indices: on the c-th match, keep it
        with probability 1/c for a uniform choice among all matches.

        Algorithm:
        - Scan nums; when val==target: count++; with prob 1/count set chosen=i.

        Complexity: O(n) time, O(1) extra space.
        """
        chosen = -1
        count = 0
        for i, val in enumerate(self.nums):
            if val == target:
                count += 1
                if random.randrange(count) == 0:
                    chosen = i
        return chosen


# Your Solution object will be instantiated and called as such:
# obj = Solution(nums)
# param_1 = obj.pick(target)
# @lc code=end
