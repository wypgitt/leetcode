#
# @lc app=leetcode id=2182 lang=python3
#
# [2182] Construct String With Repeat Limit
#
# https://leetcode.com/problems/construct-string-with-repeat-limit/description/
#
# algorithms
# Medium (70.80%)
# Likes:    1293
# Dislikes: 103
# Total Accepted:    133.1K
# Total Submissions: 188K
# Testcase Example:  "\"cczazcc\"\n3"
#
# You are given a string s and an integer repeatLimit. Construct a new string
# repeatLimitedString using the characters of s such that no letter appears more
# than repeatLimit times in a row. You do not have to use all characters from s.
#
# Return the lexicographically largest repeatLimitedString possible.
#
# A string a is lexicographically larger than a string b if in the first
# position where a and b differ, string a has a letter that appears later in the
# alphabet than the corresponding letter in b. If the first min(a.length,
# b.length) characters do not differ, then the longer string is the
# lexicographically larger one.
#
#
#
# Example 1:
#
# Input: s = "cczazcc", repeatLimit = 3
# Output: "zzcccac"
# Explanation: We use all of the characters from s to construct the
# repeatLimitedString "zzcccac".
# The letter 'a' appears at most 1 time in a row.
# The letter 'c' appears at most 3 times in a row.
# The letter 'z' appears at most 2 times in a row.
# Hence, no letter appears more than repeatLimit times in a row and the string
# is a valid repeatLimitedString.
# The string is the lexicographically largest repeatLimitedString possible so we
# return "zzcccac".
# Note that the string "zzcccca" is lexicographically larger but the letter 'c'
# appears more than 3 times in a row, so it is not a valid repeatLimitedString.
#
# Example 2:
#
# Input: s = "aababab", repeatLimit = 2
# Output: "bbabaa"
# Explanation: We use only some of the characters from s to construct the
# repeatLimitedString "bbabaa".
# The letter 'a' appears at most 2 times in a row.
# The letter 'b' appears at most 2 times in a row.
# Hence, no letter appears more than repeatLimit times in a row and the string
# is a valid repeatLimitedString.
# The string is the lexicographically largest repeatLimitedString possible so we
# return "bbabaa".
# Note that the string "bbabaaa" is lexicographically larger but the letter 'a'
# appears more than 2 times in a row, so it is not a valid repeatLimitedString.
#
#
#
# Constraints:
#
#
# 1 <= repeatLimit <= s.length <= 10^5
#
#
# s consists of lowercase English letters.
#

# @lc code=start
from collections import Counter
import heapq


class Solution:
    def repeatLimitedString(self, s: str, repeatLimit: int) -> str:
        """
        Interview explanation:
        Build lexicographically largest string using chars of s, with no char
        repeating more than repeatLimit times consecutively.

        Algorithm:
        (greedy + max-heap)
        - Max-heap by char; pop largest; append up to min(count, repeatLimit);
          if still remaining, peek next largest to break streak (append one),
          then push both back.

        Complexity: O(n log 26) time, O(1)/O(sigma) space.
        """
        cnt = Counter(s)
        heap = [(-ord(c), c, k) for c, k in cnt.items()]
        heapq.heapify(heap)
        ans = []
        while heap:
            _, c, k = heapq.heappop(heap)
            use = min(k, repeatLimit)
            ans.append(c * use)
            k -= use
            if k == 0:
                continue
            if not heap:
                break
            _, c2, k2 = heapq.heappop(heap)
            ans.append(c2)
            k2 -= 1
            if k2:
                heapq.heappush(heap, (-ord(c2), c2, k2))
            heapq.heappush(heap, (-ord(c), c, k))
        return "".join(ans)
# @lc code=end
