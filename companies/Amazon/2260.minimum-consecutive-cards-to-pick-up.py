#
# @lc app=leetcode id=2260 lang=python3
#
# [2260] Minimum Consecutive Cards to Pick Up
#
# https://leetcode.com/problems/minimum-consecutive-cards-to-pick-up/description/
#
# algorithms
# Medium (53.97%)
# Likes:    1101
# Dislikes: 45
# Total Accepted:    125.1K
# Total Submissions: 231.9K
# Testcase Example:  "[3,4,2,3,4,7]"
#
# You are given an integer array cards where cards[i] represents the value of
# the i^th card. A pair of cards are matching if the cards have the same value.
#
# Return the minimum number of consecutive cards you have to pick up to have a
# pair of matching cards among the picked cards. If it is impossible to have
# matching cards, return -1.
#
#
#
# Example 1:
#
# Input: cards = [3,4,2,3,4,7]
# Output: 4
# Explanation: We can pick up the cards [3,4,2,3] which contain a matching pair
# of cards with value 3. Note that picking up the cards [4,2,3,4] is also
# optimal.
#
# Example 2:
#
# Input: cards = [1,0,5,3]
# Output: -1
# Explanation: There is no way to pick up a set of consecutive cards that
# contain a pair of matching cards.
#
#
#
# Constraints:
#
#
# 1 <= cards.length <= 10^5
#
#
# 0 <= cards[i] <= 10^6
#

# @lc code=start
from typing import List
from collections import defaultdict


class Solution:
    def minimumCardPickup(self, cards: List[int]) -> int:
        """
        Interview explanation:
        Shortest subarray containing a duplicate card value; -1 if none.

        Algorithm:
        - Map last index of each value; track min (i - last + 1).

        Complexity: O(n) time, O(n) space.
        """
        last = {}
        ans = float("inf")
        for i, c in enumerate(cards):
            if c in last:
                ans = min(ans, i - last[c] + 1)
            last[c] = i
        return -1 if ans == float("inf") else ans

    def minimumCardPickup_two_pointers(self, cards: List[int]) -> int:
        """
        Interview explanation:
        Sliding-window alternate: expand until duplicate, shrink left.

        Algorithm:
        - Window with counts; when any count>1 update min length and shrink.

        Complexity: O(n) time, O(n) space.
        """
        cnt = defaultdict(int)
        left = 0
        ans = float("inf")
        for right, c in enumerate(cards):
            cnt[c] += 1
            while cnt[c] > 1:
                ans = min(ans, right - left + 1)
                cnt[cards[left]] -= 1
                left += 1
        return -1 if ans == float("inf") else ans
# @lc code=end
