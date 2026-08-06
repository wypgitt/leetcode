#
# @lc app=leetcode id=691 lang=python3
#
# [691] Stickers to Spell Word
#
# https://leetcode.com/problems/stickers-to-spell-word/description/
#
# algorithms
# Hard (51.06%)
# Likes:    1342
# Dislikes: 130
# Total Accepted:    98.5K
# Total Submissions: 193K
# Testcase Example:  "[\"with\",\"example\",\"science\"]"
#
# We are given n different types of stickers. Each sticker has a lowercase
# English word on it.
#
# You would like to spell out the given string target by cutting individual
# letters from your collection of stickers and rearranging them. You can use
# each sticker more than once if you want, and you have infinite quantities of
# each sticker.
#
# Return the minimum number of stickers that you need to spell out target. If
# the task is impossible, return -1.
#
# Note: In all test cases, all words were chosen randomly from the 1000 most
# common US English words, and target was chosen as a concatenation of two
# random words.
#
# Example 1:
#
# Input: stickers = ["with","example","science"], target = "thehat"
# Output: 3
# Explanation:
# We can use 2 "with" stickers, and 1 "example" sticker.
# After cutting and rearrange the letters of those stickers, we can form the
# target "thehat".
# Also, this is the minimum number of stickers necessary to form the target
# string.
#
# Example 2:
#
# Input: stickers = ["notice","possible"], target = "basicbasic"
# Output: -1
# Explanation:
# We cannot form the target "basicbasic" from cutting letters from the given
# stickers.
#
# Constraints:
#
# n == stickers.length
#
# 1 <= n <= 50
#
# 1 <= stickers[i].length <= 10
#
# 1 <= target.length <= 15
#
# stickers[i] and target consist of lowercase English letters.
#

# @lc code=start
from collections import Counter
from functools import lru_cache
from typing import List


class Solution:
    def minStickers(self, stickers: List[str], target: str) -> int:
        """
        Interview explanation:
        Min stickers (with letter multisets) to form target. DP on remaining
        target subsequence / bitmask of unused target chars. For each state,
        try every sticker that covers at least one needed letter.

        Algorithm:
        - Represent remaining target as a sorted string of still-needed letters.
        - dp(remain): try each sticker, subtract counts, recurse; take min + 1.
        - Return -1 if impossible.

        Complexity: O(|stickers| * |target|! / symmetries) ~ O(S * 3^T) style;
        with string states dominated by distinct subsequences. Practical with memo.
        """
        target_set = set(target)
        stick_cnts = [Counter(s) for s in stickers if set(s) & target_set]
        if not stick_cnts and target:
            return -1

        @lru_cache(None)
        def dp(remain: str) -> int:
            if not remain:
                return 0
            need = Counter(remain)
            ans = float("inf")
            for sc in stick_cnts:
                if remain[0] not in sc:
                    continue
                nxt = []
                for ch, cnt in need.items():
                    left = cnt - sc.get(ch, 0)
                    if left > 0:
                        nxt.append(ch * left)
                res = dp("".join(nxt))
                if res >= 0:
                    ans = min(ans, 1 + res)
            return -1 if ans == float("inf") else int(ans)

        return dp("".join(sorted(target)))
# @lc code=end
