#
# @lc app=leetcode id=1423 lang=python3
#
# [1423] Maximum Points You Can Obtain from Cards
#
# https://leetcode.com/problems/maximum-points-you-can-obtain-from-cards/description/
#
# algorithms
# Medium (58.18%)
# Likes:    7214
# Dislikes: 330
# Total Accepted:    567K
# Total Submissions: 974K
# Testcase Example:  "[1,2,3,4,5,6,1]"
#
# There are several cards arranged in a row, and each card has an associated
# number of points. The points are given in the integer array cardPoints.
#
# In one step, you can take one card from the beginning or from the end of the
# row. You have to take exactly k cards.
#
# Your score is the sum of the points of the cards you have taken.
#
# Given the integer array cardPoints and the integer k, return the maximum
# score you can obtain.
#
# Example 1:
#
# Input: cardPoints = [1,2,3,4,5,6,1], k = 3
# Output: 12
# Explanation: After the first step, your score will always be 1. However,
# choosing the rightmost card first will maximize your total score. The optimal
# strategy is to take the three cards on the right, giving a final score of 1 +
# 6 + 5 = 12.
#
# Example 2:
#
# Input: cardPoints = [2,2,2], k = 2
# Output: 4
# Explanation: Regardless of which two cards you take, your score will always
# be 4.
#
# Example 3:
#
# Input: cardPoints = [9,7,7,9,7,7,9], k = 7
# Output: 55
# Explanation: You have to take all the cards. Your score is the sum of points
# of all cards.
#
# Constraints:
#
# 1 <= cardPoints.length <= 10^5
#
# 1 <= cardPoints[i] <= 10^4
#
# 1 <= k <= cardPoints.length
#

# @lc code=start
from typing import List


class Solution:
    def maxScore(self, cardPoints: List[int], k: int) -> int:
        """
        Interview explanation:
        Take k cards from ends only ≡ leave a contiguous subarray of length
        n-k unused. Maximize taken sum = total - min sum of window length n-k.

        Algorithm:
        (sliding window)
        - total=sum; if k==n return total; find min window sum of len n-k; return total-min.

        Complexity: O(n) time, O(1) space.
        """
        n = len(cardPoints)
        total = sum(cardPoints)
        if k == n:
            return total
        need = n - k
        window = sum(cardPoints[:need])
        mn = window
        for i in range(need, n):
            window += cardPoints[i] - cardPoints[i - need]
            mn = min(mn, window)
        return total - mn

    def maxScore_prefix(self, cardPoints: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: try taking i from left and k-i from right via prefix/suffix sums.

        Algorithm:
        - left_pref; for i=0..k: score = left[i] + right[k-i]; track max.

        Complexity: O(n) time, O(k) space.
        """
        n = len(cardPoints)
        left = [0] * (k + 1)
        right = [0] * (k + 1)
        for i in range(1, k + 1):
            left[i] = left[i - 1] + cardPoints[i - 1]
            right[i] = right[i - 1] + cardPoints[n - i]
        return max(left[i] + right[k - i] for i in range(k + 1))
# @lc code=end
