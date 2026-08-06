#
# @lc app=leetcode id=1405 lang=python3
#
# [1405] Longest Happy String
#
# https://leetcode.com/problems/longest-happy-string/description/
#
# algorithms
# Medium (65.53%)
# Likes:    2829
# Dislikes: 322
# Total Accepted:    225K
# Total Submissions: 343K
# Testcase Example:  "1"
#
# A string s is called happy if it satisfies the following conditions:
#
# s only contains the letters 'a', 'b', and 'c'.
#
# s does not contain any of "aaa", "bbb", or "ccc" as a substring.
#
# s contains at most a occurrences of the letter 'a'.
#
# s contains at most b occurrences of the letter 'b'.
#
# s contains at most c occurrences of the letter 'c'.
#
# Given three integers a, b, and c, return the longest possible happy string.
# If there are multiple longest happy strings, return any of them. If there is
# no such string, return the empty string "".
#
# A substring is a contiguous sequence of characters within a string.
#
# Example 1:
#
# Input: a = 1, b = 1, c = 7
# Output: "ccaccbcc"
# Explanation: "ccbccacc" would also be a correct answer.
#
# Example 2:
#
# Input: a = 7, b = 1, c = 0
# Output: "aabaa"
# Explanation: It is the only correct answer in this case.
#
# Constraints:
#
# 0 <= a, b, c <= 100
#
# a + b + c > 0
#

# @lc code=start
import heapq


class Solution:
    def longestDiverseString(self, a: int, b: int, c: int) -> str:
        """
        Interview explanation:
        Build longest string with at most a/b/c of each letter and no three
        identical letters in a row. Always append the currently most remaining
        letter that won't form "xxx"; if blocked, try the second most.

        Algorithm:
        (max-heap greedy)
        - Heap of (-count, char); while heap: pop largest; if last two same as it,
          pop second; append; push back leftover counts.

        Complexity: O((a+b+c) log 3) ≈ O(a+b+c) time, O(1) space.
        """
        heap = []
        for cnt, ch in ((a, "a"), (b, "b"), (c, "c")):
            if cnt:
                heapq.heappush(heap, (-cnt, ch))
        res = []
        while heap:
            cnt, ch = heapq.heappop(heap)
            if len(res) >= 2 and res[-1] == res[-2] == ch:
                if not heap:
                    break
                cnt2, ch2 = heapq.heappop(heap)
                res.append(ch2)
                if cnt2 + 1 < 0:
                    heapq.heappush(heap, (cnt2 + 1, ch2))
                heapq.heappush(heap, (cnt, ch))
            else:
                res.append(ch)
                if cnt + 1 < 0:
                    heapq.heappush(heap, (cnt + 1, ch))
        return "".join(res)

    def longestDiverseString_sort(self, a: int, b: int, c: int) -> str:
        """
        Interview explanation:
        Alternate greedy: repeatedly pick from sorted (count,char) without heap.

        Algorithm:
        - While True: sort three counts; try append max if not creating xxx;
          else next; stop when none appendable.

        Complexity: O((a+b+c) * 3 log 3) time, O(1) space.
        """
        cnt = [["a", a], ["b", b], ["c", c]]
        res = []
        while True:
            cnt.sort(key=lambda x: -x[1])
            placed = False
            for i in range(3):
                if cnt[i][1] == 0:
                    continue
                if len(res) >= 2 and res[-1] == res[-2] == cnt[i][0]:
                    continue
                res.append(cnt[i][0])
                cnt[i][1] -= 1
                placed = True
                break
            if not placed:
                break
        return "".join(res)
# @lc code=end
