#
# @lc app=leetcode id=3907 lang=python3
#
# [3907] Count Smaller Elements With Opposite Parity
#
# https://leetcode.com/problems/count-smaller-elements-with-opposite-parity/description/
#
# algorithms
# Medium (73.81%)
# Likes:    1
# Dislikes: 1
# Total Accepted:    358
# Total Submissions: 485
# Testcase Example:  "[5,2,4,1,3]"
#
#
# You are given an integer array nums of length n.
#
# The score of an index i is defined as the number of indices j such that:
#
# i < j < n
#
# nums[j] < nums[i]
#
# nums[i] and nums[j] have different parity (one is even and the other is
# odd).
#
# Return an integer array answer of length n, where answer[i] is the score
# of index i.
#
# Example 1:
#
# Input: nums = [5,2,4,1,3]
#
# Output: [2,1,2,0,0]
#
# Explanation:
#
# For i = 0, the elements nums[1] = 2 and nums[2] = 4 are smaller and have
# different parity.
#
# For i = 1, the element nums[3] = 1 is smaller and has different parity.
#
# For i = 2, the elements nums[3] = 1 and nums[4] = 3 are smaller and have
# different parity.
#
# No valid elements exist for the remaining indices.
#
# Thus, the answer = [2, 1, 2, 0, 0].
#
# Example 2:
#
# Input: nums = [4,4,1]
#
# Output: [1,1,0]
#
# Explanation:​​​​​​​
#
# For i = 0 and i = 1, the element nums[2] = 1 is smaller and has
# different parity. Thus, the answer = [1, 1, 0].
#
# Example 3:
#
# Input: nums = [7]
#
# Output: [0]
#
# Explanation:
#
# No elements exist to the right of index 0, so its score is 0. Thus, the
# answer = [0].
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9​​​​​​​
#

# @lc code=start
from typing import List


class Fenwick:
    def __init__(self, size: int) -> None:
        """
        Interview explanation:
        Fenwick tree for prefix frequency sums over compressed ranks.

        Algorithm:
        - 1-indexed array of size+1 zeros.

        Complexity: O(size) space.
        """
        self.tree = [0] * (size + 1)

    def add(self, index: int, delta: int) -> None:
        """
        Interview explanation:
        Point update: add delta at rank index.

        Algorithm:
        - Standard BIT climb by lowbit.

        Complexity: O(log n) time, O(1) space.
        """
        while index < len(self.tree):
            self.tree[index] += delta
            index += index & -index

    def query(self, index: int) -> int:
        """
        Interview explanation:
        Prefix sum of ranks in [1, index].

        Algorithm:
        - Standard BIT descend by lowbit.

        Complexity: O(log n) time, O(1) space.
        """
        total = 0
        while index > 0:
            total += self.tree[index]
            index -= index & -index
        return total


class Solution:
    def countSmallerOppositeParity(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        For each i, count j > i with nums[j] < nums[i] and opposite parity.

        Algorithm:
        - Coordinate-compress values; maintain two Fenwick trees (even/odd).
        - Scan right to left: query opposite-parity tree for ranks < nums[i],
          then insert nums[i] into its parity tree.

        Complexity: O(n log n) time, O(n) space.
        """
        values = sorted(set(nums))
        rank = {value: index + 1 for index, value in enumerate(values)}

        even_tree = Fenwick(len(values))
        odd_tree = Fenwick(len(values))
        answer = [0] * len(nums)

        for i in range(len(nums) - 1, -1, -1):
            value = nums[i]
            pos = rank[value]

            if value % 2 == 0:
                answer[i] = odd_tree.query(pos - 1)
                even_tree.add(pos, 1)
            else:
                answer[i] = even_tree.query(pos - 1)
                odd_tree.add(pos, 1)

        return answer
# @lc code=end
