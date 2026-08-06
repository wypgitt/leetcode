#
# @lc app=leetcode id=846 lang=python3
#
# [846] Hand of Straights
#
# https://leetcode.com/problems/hand-of-straights/description/
#
# algorithms
# Medium (58.28%)
# Likes:    3805
# Dislikes: 300
# Total Accepted:    478K
# Total Submissions: 820K
# Testcase Example:  "[1,2,3,6,2,3,4,7,8]"
#
# Alice has some number of cards and she wants to rearrange the cards into
# groups so that each group is of size groupSize, and consists of groupSize
# consecutive cards.
#
# Given an integer array hand where hand[i] is the value written on the i^th
# card and an integer groupSize, return true if she can rearrange the cards, or
# false otherwise.
#
# Example 1:
#
# Input: hand = [1,2,3,6,2,3,4,7,8], groupSize = 3
# Output: true
# Explanation: Alice's hand can be rearranged as [1,2,3],[2,3,4],[6,7,8]
#
# Example 2:
#
# Input: hand = [1,2,3,4,5], groupSize = 4
# Output: false
# Explanation: Alice's hand can not be rearranged into groups of 4.
#
# Constraints:
#
# 1 <= hand.length <= 10^4
#
# 0 <= hand[i] <= 10^9
#
# 1 <= groupSize <= hand.length
#
# Note: This question is the same as 1296:
# https://leetcode.com/problems/divide-array-in-sets-of-k-consecutive-numbers/
#

# @lc code=start

from typing import List
from collections import Counter
import heapq


class Solution:
    def isNStraightHand(self, hand: List[int], groupSize: int) -> bool:
        """
        Interview explanation:
        Partition into groups of groupSize consecutive values. Count frequencies;
        always start a group from the smallest remaining card.

        Algorithm (Counter + greedy):
        - If n % groupSize: False. For each start in sorted keys, while cnt[start]:
          consume start..start+g-1 or fail.

        Complexity: O(n log n) with sorted keys, O(n) space.
        """
        if len(hand) % groupSize:
            return False
        cnt = Counter(hand)
        for start in sorted(cnt):
            need = cnt[start]
            if need == 0:
                continue
            for x in range(start, start + groupSize):
                if cnt[x] < need:
                    return False
                cnt[x] -= need
        return True

    def isNStraightHand_heap(self, hand: List[int], groupSize: int) -> bool:
        """
        Interview explanation:
        Heap of distinct values for O(log n) next-minimum extraction — equally
        classic greedy with Counter.

        Algorithm:
        - Counter + min-heap of keys; pop exhausted keys; start groups from
          heap[0]; decrement consecutive counts.

        Complexity: O(n log n) time, O(n) space.
        """
        if len(hand) % groupSize:
            return False
        cnt = Counter(hand)
        heap = list(cnt.keys())
        heapq.heapify(heap)
        while heap:
            while heap and cnt[heap[0]] == 0:
                heapq.heappop(heap)
            if not heap:
                break
            start = heap[0]
            for x in range(start, start + groupSize):
                if cnt[x] == 0:
                    return False
                cnt[x] -= 1
        return True
# @lc code=end
