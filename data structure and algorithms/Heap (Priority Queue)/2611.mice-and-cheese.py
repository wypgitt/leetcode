#
# @lc app=leetcode id=2611 lang=python3
#
# [2611] Mice and Cheese
#
# https://leetcode.com/problems/mice-and-cheese/description/
#
# algorithms
# Medium (48.79%)
# Likes:    684
# Dislikes: 75
# Total Accepted:    40.7K
# Total Submissions: 83.3K
# Testcase Example:  "[1,1,3,4]\n[4,4,1,1]\n2"
#
# There are two mice and n different types of cheese, each type of cheese should
# be eaten by exactly one mouse.
#
# A point of the cheese with index i (0-indexed) is:
#
#
# reward1[i] if the first mouse eats it.
#
#
# reward2[i] if the second mouse eats it.
#
# You are given a positive integer array reward1, a positive integer array
# reward2, and a non-negative integer k.
#
# Return the maximum points the mice can achieve if the first mouse eats exactly
# k types of cheese.
#
#
#
# Example 1:
#
# Input: reward1 = [1,1,3,4], reward2 = [4,4,1,1], k = 2
# Output: 15
# Explanation: In this example, the first mouse eats the 2^nd (0-indexed) and
# the 3^rd types of cheese, and the second mouse eats the 0^th and the 1^st
# types of cheese.
# The total points are 4 + 4 + 3 + 4 = 15.
# It can be proven that 15 is the maximum total points that the mice can
# achieve.
#
# Example 2:
#
# Input: reward1 = [1,1], reward2 = [1,1], k = 2
# Output: 2
# Explanation: In this example, the first mouse eats the 0^th (0-indexed) and
# 1^st types of cheese, and the second mouse does not eat any cheese.
# The total points are 1 + 1 = 2.
# It can be proven that 2 is the maximum total points that the mice can achieve.
#
#
#
# Constraints:
#
#
# 1 <= n == reward1.length == reward2.length <= 10^5
#
#
# 1 <= reward1[i], reward2[i] <= 1000
#
#
# 0 <= k <= n
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def miceAndCheese(self, reward1: List[int], reward2: List[int], k: int) -> int:
        """
        Interview explanation:
        First mouse eats exactly k cheeses; maximize total points.
        Equivalent to giving all to mouse 2, then switching the k best gains
        (reward1[i] - reward2[i]) to mouse 1.

        Algorithm:
        - Start with sum(reward2); add the top k differences reward1-reward2.

        Complexity: O(n log n) time, O(n) space.
        """
        diffs = [a - b for a, b in zip(reward1, reward2)]
        diffs.sort(reverse=True)
        return sum(reward2) + sum(diffs[:k])

    def miceAndCheese_heap(self, reward1: List[int], reward2: List[int], k: int) -> int:
        """
        Interview explanation:
        Same gain idea using a heap of size k (or nlargest) for top differences.

        Algorithm:
        - sum(reward2) + sum of k largest (reward1[i] - reward2[i]).

        Complexity: O(n log k) time, O(k) space.
        """
        return sum(reward2) + sum(heapq.nlargest(k, (a - b for a, b in zip(reward1, reward2))))
# @lc code=end
