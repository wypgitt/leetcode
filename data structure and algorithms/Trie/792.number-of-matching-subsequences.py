#
# @lc app=leetcode id=792 lang=python3
#
# [792] Number of Matching Subsequences
#
# https://leetcode.com/problems/number-of-matching-subsequences/description/
#
# algorithms
# Medium (50.58%)
# Likes:    5845
# Dislikes: 249
# Total Accepted:    282K
# Total Submissions: 557K
# Testcase Example:  "\"abcde\""
#
# Given a string s and an array of strings words, return the number of words[i]
# that is a subsequence of s.
#
# A subsequence of a string is a new string generated from the original string
# with some characters (can be none) deleted without changing the relative
# order of the remaining characters.
#
# For example, "ace" is a subsequence of "abcde".
#
# Example 1:
#
# Input: s = "abcde", words = ["a","bb","acd","ace"]
# Output: 3
# Explanation: There are three strings in words that are a subsequence of s:
# "a", "acd", "ace".
#
# Example 2:
#
# Input: s = "dsahjpjauf", words = ["ahjpjau","ja","ahbwzgqnuk","tnmlanowax"]
# Output: 2
#
# Constraints:
#
# 1 <= s.length <= 5 * 10^4
#
# 1 <= words.length <= 5000
#
# 1 <= words[i].length <= 50
#
# s and words[i] consist of only lowercase English letters.
#

# @lc code=start
from bisect import bisect_left
from collections import defaultdict, deque
from typing import List


class Solution:
    def numMatchingSubseq(self, s: str, words: List[str]) -> int:
        """
        Interview explanation:
        Count words that are subsequences of s. Bucket words by next needed
        char ("next pointers"): for each char c in s, advance all words waiting
        on c; if finished, count++ else re-bucket by their new next char.

        Algorithm:
        - waiting[c] = deque of iterators/indices into words needing c.
        - For ch in s: process waiting[ch]; advance each.
        - Return count of completed words.

        Complexity: O(|s| + total length of words) time, O(total words len) space.
        """
        waiting = defaultdict(deque)
        for w in words:
            it = iter(w)
            waiting[next(it)].append(it)
        ans = 0
        for ch in s:
            for _ in range(len(waiting[ch])):
                it = waiting[ch].popleft()
                nxt = next(it, None)
                if nxt is None:
                    ans += 1
                else:
                    waiting[nxt].append(it)
        return ans

    def numMatchingSubseq_binary_search(self, s: str, words: List[str]) -> int:
        """
        Interview explanation:
        Alternate: index positions of each char in s; for a word, greedily
        pick next occurrence via binary search (bisect) after previous index.

        Algorithm:
        - pos[c] = sorted list of indices of c in s.
        - For each word: cur = -1; for char: bisect_left(pos[char], cur+1);
          fail if none.
        - Count successes.

        Complexity: O(|s| + sum(|w| log |s|)) time, O(|s|) space.
        """
        pos = defaultdict(list)
        for i, ch in enumerate(s):
            pos[ch].append(i)

        def is_subseq(w: str) -> bool:
            cur = -1
            for ch in w:
                idxs = pos[ch]
                j = bisect_left(idxs, cur + 1)
                if j == len(idxs):
                    return False
                cur = idxs[j]
            return True

        return sum(1 for w in words if is_subseq(w))
# @lc code=end

