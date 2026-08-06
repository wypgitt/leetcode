#
# @lc app=leetcode id=888 lang=python3
#
# [888] Fair Candy Swap
#
# https://leetcode.com/problems/fair-candy-swap/description/
#
# algorithms
# Easy (65.4%)
# Likes:    2301
# Dislikes: 425
# Total Accepted:    180K
# Total Submissions: 275K
# Testcase Example:  "[1,1]"
#
# Alice and Bob have a different total number of candies. You are given two
# integer arrays aliceSizes and bobSizes where aliceSizes[i] is the number of
# candies of the i^th box of candy that Alice has and bobSizes[j] is the number
# of candies of the j^th box of candy that Bob has.
#
# Since they are friends, they would like to exchange one candy box each so
# that after the exchange, they both have the same total amount of candy. The
# total amount of candy a person has is the sum of the number of candies in
# each box they have.
#
# Return an integer array answer where answer[0] is the number of candies in
# the box that Alice must exchange, and answer[1] is the number of candies in
# the box that Bob must exchange. If there are multiple answers, you may return
# any one of them. It is guaranteed that at least one answer exists.
#
# Example 1:
#
# Input: aliceSizes = [1,1], bobSizes = [2,2]
# Output: [1,2]
#
# Example 2:
#
# Input: aliceSizes = [1,2], bobSizes = [2,3]
# Output: [1,2]
#
# Example 3:
#
# Input: aliceSizes = [2], bobSizes = [1,3]
# Output: [2,3]
#
# Constraints:
#
# 1 <= aliceSizes.length, bobSizes.length <= 10^4
#
# 1 <= aliceSizes[i], bobSizes[j] <= 10^5
#
# Alice and Bob have a different total number of candies.
#
# There will be at least one valid answer for the given input.
#

# @lc code=start
from typing import List


class Solution:
    def fairCandySwap(self, aliceSizes: List[int], bobSizes: List[int]) -> List[int]:
        """
        Interview explanation:
        Need Sa - x + y = Sb - y + x ⇒ y - x = (Sb-Sa)/2. For each Alice candy
        x, look for Bob candy y = x + diff in a set.

        Algorithm:
        - diff = (sumB - sumA) // 2; setB = set(bob). For x in alice: if
          x+diff in setB return [x, x+diff].

        Complexity: O(n+m) time, O(m) space.
        """
        sum_a, sum_b = sum(aliceSizes), sum(bobSizes)
        diff = (sum_b - sum_a) // 2
        set_b = set(bobSizes)
        for x in aliceSizes:
            if x + diff in set_b:
                return [x, x + diff]
        return []
# @lc code=end

