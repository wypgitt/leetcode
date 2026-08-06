#
# @lc app=leetcode id=384 lang=python3
#
# [384] Shuffle an Array
#
# https://leetcode.com/problems/shuffle-an-array/description/
#
# algorithms
# Medium (59.91%)
# Likes:    1449
# Dislikes: 946
# Total Accepted:    402K
# Total Submissions: 671K
# Testcase Example:  "[\"Solution\",\"shuffle\",\"reset\",\"shuffle\"]"
#
# Given an integer array nums, design an algorithm to randomly shuffle the
# array. All permutations of the array should be equally likely as a result of
# the shuffling.
#
# Implement the Solution class:
#
# Solution(int[] nums) Initializes the object with the integer array nums.
#
# int[] reset() Resets the array to its original configuration and returns it.
#
# int[] shuffle() Returns a random shuffling of the array.
#
# Example 1:
#
# Input
# ["Solution", "shuffle", "reset", "shuffle"]
# [[[1, 2, 3]], [], [], []]
# Output
# [null, [3, 1, 2], [1, 2, 3], [1, 3, 2]]
#
# Explanation
# Solution solution = new Solution([1, 2, 3]);
# solution.shuffle(); // Shuffle the array [1,2,3] and return its result.
# // Any permutation of [1,2,3] must be equally likely to be returned.
# // Example: return [3, 1, 2]
# solution.reset(); // Resets the array back to its original configuration
# [1,2,3]. Return [1, 2, 3]
# solution.shuffle(); // Returns the random shuffling of array [1,2,3].
# Example: return [1, 3, 2]
#
# Constraints:
#
# 1 <= nums.length <= 50
#
# -10^6 <= nums[i] <= 10^6
#
# All the elements of nums are unique.
#
# At most 10^4 calls in total will be made to reset and shuffle.
#

# @lc code=start
import random
from typing import List


class Solution:
    """
    Interview explanation:
    Fisher–Yates shuffle for uniform random permutations. Keep original copy
    for reset; shuffle works on a mutable copy.

    Algorithm:
    - __init__: store nums and a working copy.
    - reset: restore from original.
    - shuffle: for i from n-1..1, swap i with random index in [0, i].

    Complexity: O(n) per shuffle/reset, O(n) space.
    """

    def __init__(self, nums: List[int]):
        """
        Interview explanation:
        Keep an immutable original copy for reset and a working array for shuffle.

        Algorithm:
        - original = nums[:]; arr = nums[:].

        Complexity: O(n) time and space.
        """
        self.original = nums[:]
        self.arr = nums[:]

    def reset(self) -> List[int]:
        """
        Interview explanation:
        Restore the working array from the saved original configuration.

        Algorithm:
        - arr = original[:]; return arr.

        Complexity: O(n) time and space for the copy.
        """
        self.arr = self.original[:]
        return self.arr

    def shuffle(self) -> List[int]:
        """
        Interview explanation:
        Fisher–Yates: for each suffix position, swap with a uniform random
        earlier index so every permutation is equally likely.

        Algorithm:
        - For i from n-1 down to 1: j = randint(0, i); swap arr[i], arr[j].

        Complexity: O(n) time, O(1) extra space.
        """
        a = self.arr
        for i in range(len(a) - 1, 0, -1):
            j = random.randint(0, i)
            a[i], a[j] = a[j], a[i]
        return a


# Your Solution object will be instantiated and called as such:
# obj = Solution(nums)
# param_1 = obj.reset()
# param_2 = obj.shuffle()
# @lc code=end
