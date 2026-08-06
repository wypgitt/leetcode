#
# @lc app=leetcode id=135 lang=python3
#
# [135] Candy
#
# https://leetcode.com/problems/candy/description/
#
# algorithms
# Hard (48.97%)
# Likes:    9472
# Dislikes: 863
# Total Accepted:    1.1M
# Total Submissions: 2.3M
# Testcase Example:  "[1,0,2]"
#
# There are n children standing in a line. Each child is assigned a rating
# value given in the integer array ratings.
#
# You are giving candies to these children subjected to the following
# requirements:
#
# Each child must have at least one candy.
#
# Children with a higher rating get more candies than their neighbors.
#
# Return the minimum number of candies you need to have to distribute the
# candies to the children.
#
# Example 1:
#
# Input: ratings = [1,0,2]
# Output: 5
# Explanation: You can allocate to the first, second and third child with 2, 1,
# 2 candies respectively.
#
# Example 2:
#
# Input: ratings = [1,2,2]
# Output: 4
# Explanation: You can allocate to the first, second and third child with 1, 2,
# 1 candies respectively.
# The third child gets 1 candy because it satisfies the above two conditions.
#
# Constraints:
#
# n == ratings.length
#
# 1 <= n <= 2 * 10^4
#
# 0 <= ratings[i] <= 2 * 10^4
#

# @lc code=start
from typing import List


class Solution:
    def candy(self, ratings: List[int]) -> int:
        """
        Interview explanation:
        Two-pass greedy: enforce the left-neighbor constraint left-to-right,
        then the right-neighbor constraint right-to-left, taking maxima so both
        sides stay satisfied with the fewest candies.

        Algorithm:
        - Start with 1 candy each.
        - Left pass: if ratings[i] > ratings[i-1], candies[i] = candies[i-1] + 1.
        - Right pass: if ratings[i] > ratings[i+1],
          candies[i] = max(candies[i], candies[i+1] + 1).
        - Return sum(candies).

        Complexity: O(n) time, O(n) space.
        """
        n = len(ratings)
        candies = [1] * n
        for i in range(1, n):
            if ratings[i] > ratings[i - 1]:
                candies[i] = candies[i - 1] + 1
        for i in range(n - 2, -1, -1):
            if ratings[i] > ratings[i + 1]:
                candies[i] = max(candies[i], candies[i + 1] + 1)
        return sum(candies)
# @lc code=end
