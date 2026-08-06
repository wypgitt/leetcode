#
# @lc app=leetcode id=936 lang=python3
#
# [936] Stamping The Sequence
#
# https://leetcode.com/problems/stamping-the-sequence/description/
#
# algorithms
# Hard (62.28%)
# Likes:    1584
# Dislikes: 222
# Total Accepted:    65.6K
# Total Submissions: 105K
# Testcase Example:  "\"abc\""
#
# You are given two strings stamp and target. Initially, there is a string s of
# length target.length with all s[i] == '?'.
#
# In one turn, you can place stamp over s and replace every letter in the s
# with the corresponding letter from stamp.
#
# For example, if stamp = "abc" and target = "abcba", then s is "?????"
# initially. In one turn you can:
#
# place stamp at index 0 of s to obtain "abc??",
#
# place stamp at index 1 of s to obtain "?abc?", or
#
# place stamp at index 2 of s to obtain "??abc".
#
# Note that stamp must be fully contained in the boundaries of s in order to
# stamp (i.e., you cannot place stamp at index 3 of s).
#
# We want to convert s to target using at most 10 * target.length turns.
#
# Return an array of the index of the left-most letter being stamped at each
# turn. If we cannot obtain target from s within 10 * target.length turns,
# return an empty array.
#
# Example 1:
#
# Input: stamp = "abc", target = "ababc"
# Output: [0,2]
# Explanation: Initially s = "?????".
# - Place stamp at index 0 to get "abc??".
# - Place stamp at index 2 to get "ababc".
# [1,0,2] would also be accepted as an answer, as well as some other answers.
#
# Example 2:
#
# Input: stamp = "abca", target = "aabcaca"
# Output: [3,0,1]
# Explanation: Initially s = "???????".
# - Place stamp at index 3 to get "???abca".
# - Place stamp at index 0 to get "abcabca".
# - Place stamp at index 1 to get "aabcaca".
#
# Constraints:
#
# 1 <= stamp.length <= target.length <= 1000
#
# stamp and target consist of lowercase English letters.
#

# @lc code=start
from typing import List


class Solution:
    def movesToStamp(self, stamp: str, target: str) -> List[int]:
        """
        Interview explanation:
        Work backwards: repeatedly find a window of target that still "matches"
        stamp (treating already- '?' as wild), replace with '?', record index.
        Reverse the list of moves for forward order. Greedy reverse-stamping.

        Algorithm:
        - t = list(target); m=len(stamp); n=len(target)
        - While not all '?': scan windows; if can_stamp(i): paint '?', append i
        - If a full pass stamps nothing → impossible []
        - Return reversed move list (at most n*10 moves per constraints)

        Complexity: O(n * (n-m+1) * m) time worst, O(n) space.
        """
        m, n = len(stamp), len(target)
        t = list(target)
        done = [False] * (n - m + 1)
        ans: List[int] = []
        made = 0

        def can_stamp(i: int) -> bool:
            has_non = False
            for j in range(m):
                if t[i + j] == '?':
                    continue
                if t[i + j] != stamp[j]:
                    return False
                has_non = True
            return has_non

        def do_stamp(i: int) -> int:
            changed = 0
            for j in range(m):
                if t[i + j] != '?':
                    t[i + j] = '?'
                    changed += 1
            return changed

        while made < n:
            progress = False
            for i in range(n - m + 1):
                if not done[i] and can_stamp(i):
                    changed = do_stamp(i)
                    made += changed
                    done[i] = True
                    ans.append(i)
                    progress = True
                    if made == n:
                        break
            if not progress:
                return []
        ans.reverse()
        return ans
# @lc code=end

