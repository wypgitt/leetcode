#
# @lc app=leetcode id=358 lang=python3
#
# [358] Rearrange String k Distance Apart
#
# https://leetcode.com/problems/rearrange-string-k-distance-apart/description/
#
# algorithms
# Hard (39.99%)
# Likes:    1002
# Dislikes: 39
# Total Accepted:    74.5K
# Total Submissions: 186.4K
# Testcase Example:  "\"aabbcc\"\n3"
#
#
# Given a string s and an integer k, rearrange s such that the same
# characters are at least distance k from each other. If it is not
# possible to rearrange the string, return an empty string "".
#
# Example 1:
#
# Input: s = "aabbcc", k = 3
# Output: "abcabc"
# Explanation: The same letters are at least a distance of 3 from each
# other.
#
# Example 2:
#
# Input: s = "aaabc", k = 3
# Output: ""
# Explanation: It is not possible to rearrange the string.
#
# Example 3:
#
# Input: s = "aaadbbcc", k = 2
# Output: "abacabcd"
# Explanation: The same letters are at least a distance of 2 from each
# other.
#
# Constraints:
#
# 1 <= s.length <= 3 * 10^5
#
# s consists of only lowercase English letters.
#
# 0 <= k <= s.length
#
# @lc code=start
import heapq
from collections import Counter, deque
from typing import List, Tuple


class Solution:
    def rearrangeString(self, s: str, k: int) -> str:
        """
        Interview explanation:
        Greedy heap: always place the currently most frequent remaining char
        that is allowed. After placing, cool it down for k-1 steps in a queue
        before returning it to the max-heap.

        Algorithm:
        - Max-heap of (-freq, char); cooldown deque of (freq, char, ready_time).
        - For each position: release cooled chars; pop heap; append char;
          if remaining, enqueue with ready = i+k.
        - Fail if heap empty before finishing.

        Complexity: O(n log 26) time, O(26) space.
        """
        if k <= 1:
            return s
        heap = [(-freq, ch) for ch, freq in Counter(s).items()]
        heapq.heapify(heap)
        wait: deque[Tuple[int, str, int]] = deque()
        res: List[str] = []
        i = 0
        while heap or wait:
            while wait and wait[0][2] <= i:
                freq, ch, _ = wait.popleft()
                heapq.heappush(heap, (-freq, ch))
            if not heap:
                return ""
            neg, ch = heapq.heappop(heap)
            res.append(ch)
            freq = -neg - 1
            if freq > 0:
                wait.append((freq, ch, i + k))
            i += 1
        return "".join(res)
# @lc code=end
