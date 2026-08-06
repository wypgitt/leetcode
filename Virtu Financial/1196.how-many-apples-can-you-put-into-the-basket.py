#
# @lc app=leetcode id=1196 lang=python3
#
# [1196] How Many Apples Can You Put into the Basket
#
# https://leetcode.com/problems/how-many-apples-can-you-put-into-the-basket/description/
#
# algorithms
# Easy (67.16%)
# Likes:    230
# Dislikes: 17
# Total Accepted:    53.4K
# Total Submissions: 79.5K
# Testcase Example:  "[100,200,150,1000]"
#
#
# You have some apples and a basket that can carry up to 5000 units of
# weight.
#
# Given an integer array weight where weight[i] is the weight of the i^th
# apple, return the maximum number of apples you can put in the basket.
#
# Example 1:
#
# Input: weight = [100,200,150,1000]
# Output: 4
# Explanation: All 4 apples can be carried by the basket since their sum
# of weights is 1450.
#
# Example 2:
#
# Input: weight = [900,950,800,1000,700,800]
# Output: 5
# Explanation: The sum of weights of the 6 apples exceeds 5000 so we
# choose any 5 of them.
#
# Constraints:
#
# 1 <= weight.length <= 10^3
#
# 1 <= weight[i] <= 10^3
#
# @lc code=start

from typing import List


class Solution:
    def maxNumberOfApples(self, weight: List[int]) -> int:
        """
        Interview explanation:
        Premium: basket holds at most 5000 units. Maximize count of apples —
        always take lightest first (greedy sort).

        Algorithm (sort):
        - Sort weight ascending; take while running sum ≤ 5000; return count.

        Complexity: O(n log n) time, O(1)/O(n) space depending on sort.
        """
        weight.sort()
        total = 0
        count = 0
        for w in weight:
            if total + w > 5000:
                break
            total += w
            count += 1
        return count
# @lc code=end
