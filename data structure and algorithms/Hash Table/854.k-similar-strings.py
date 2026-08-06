#
# @lc app=leetcode id=854 lang=python3
#
# [854] K-Similar Strings
#
# https://leetcode.com/problems/k-similar-strings/description/
#
# algorithms
# Hard (41.17%)
# Likes:    1186
# Dislikes: 63
# Total Accepted:    56.4K
# Total Submissions: 137K
# Testcase Example:  "\"ab\""
#
# Strings s1 and s2 are k-similar (for some non-negative integer k) if we can
# swap the positions of two letters in s1 exactly k times so that the resulting
# string equals s2.
#
# Given two anagrams s1 and s2, return the smallest k for which s1 and s2 are
# k-similar.
#
# Example 1:
#
# Input: s1 = "ab", s2 = "ba"
# Output: 1
# Explanation: The two string are 1-similar because we can use one swap to
# change s1 to s2: "ab" --> "ba".
#
# Example 2:
#
# Input: s1 = "abc", s2 = "bca"
# Output: 2
# Explanation: The two strings are 2-similar because we can use two swaps to
# change s1 to s2: "abc" --> "bac" --> "bca".
#
# Constraints:
#
# 1 <= s1.length <= 20
#
# s2.length == s1.length
#
# s1 and s2 contain only lowercase letters from the set {'a', 'b', 'c', 'd',
# 'e', 'f'}.
#
# s2 is an anagram of s1.
#

# @lc code=start

from collections import deque


class Solution:
    def kSimilarity(self, s1: str, s2: str) -> int:
        """
        Interview explanation:
        Minimum swaps of s1 letters to equal s2 (anagrams). Each swap can fix
        positions; BFS on string states, only swapping mismatched positions
        with a letter that belongs there (prune).

        Algorithm (BFS):
        - Start s1; while ≠ s2: find first mismatch i; try swap with j>i where
          s[j]==s2[i]; enqueue; distance = k.

        Complexity: exponential pruned; practical for n≤20.
        """
        if s1 == s2:
            return 0
        n = len(s1)
        q = deque([s1])
        seen = {s1}
        steps = 0
        target = s2
        while q:
            for _ in range(len(q)):
                cur = q.popleft()
                if cur == target:
                    return steps
                arr = list(cur)
                i = 0
                while arr[i] == target[i]:
                    i += 1
                for j in range(i + 1, n):
                    if arr[j] == target[i] and arr[j] != target[j]:
                        arr[i], arr[j] = arr[j], arr[i]
                        nxt = "".join(arr)
                        if nxt not in seen:
                            seen.add(nxt)
                            q.append(nxt)
                        arr[i], arr[j] = arr[j], arr[i]
            steps += 1
        return steps
# @lc code=end
