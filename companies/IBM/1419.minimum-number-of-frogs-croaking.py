#
# @lc app=leetcode id=1419 lang=python3
#
# [1419] Minimum Number of Frogs Croaking
#
# https://leetcode.com/problems/minimum-number-of-frogs-croaking/description/
#
# algorithms
# Medium (51.27%)
# Likes:    1130
# Dislikes: 95
# Total Accepted:    64.9K
# Total Submissions: 127K
# Testcase Example:  "\"croakcroak\""
#
# You are given the string croakOfFrogs, which represents a combination of the
# string "croak" from different frogs, that is, multiple frogs can croak at the
# same time, so multiple "croak" are mixed.
#
# Return the minimum number of different frogs to finish all the croaks in the
# given string.
#
# A valid "croak" means a frog is printing five letters 'c', 'r', 'o', 'a', and
# 'k' sequentially. The frogs have to print all five letters to finish a croak.
# If the given string is not a combination of a valid "croak" return -1.
#
# Example 1:
#
# Input: croakOfFrogs = "croakcroak"
# Output: 1
# Explanation: One frog yelling "croak" twice.
#
# Example 2:
#
# Input: croakOfFrogs = "crcoakroak"
# Output: 2
# Explanation: The minimum number of frogs is two.
# The first frog could yell "crcoakroak".
# The second frog could yell later "crcoakroak".
#
# Example 3:
#
# Input: croakOfFrogs = "croakcrook"
# Output: -1
# Explanation: The given string is an invalid combination of "croak" from
# different frogs.
#
# Constraints:
#
# 1 <= croakOfFrogs.length <= 10^5
#
# croakOfFrogs is either 'c', 'r', 'o', 'a', or 'k'.
#

# @lc code=start
class Solution:
    def minNumberOfFrogs(self, croakOfFrogs: str) -> int:
        """
        Interview explanation:
        Each frog sings c-r-o-a-k in order. Count frogs in each partial state;
        a new 'c' starts a frog (or reuses finished). Track concurrent singing;
        invalid if order broken. Answer = max concurrent.

        Algorithm:
        (state counts)
        - cnt[c,r,o,a]; on letter advance state; on 'k' finish and free a frog.
        - Track frogs_now; max over time; leftover states → -1.

        Complexity: O(n) time, O(1) space.
        """
        idx = {ch: i for i, ch in enumerate("croak")}
        cnt = [0] * 5
        frogs = ans = 0
        for ch in croakOfFrogs:
            if ch not in idx:
                return -1
            i = idx[ch]
            if i == 0:
                frogs += 1
                ans = max(ans, frogs)
                cnt[0] += 1
            else:
                if cnt[i - 1] == 0:
                    return -1
                cnt[i - 1] -= 1
                if i == 4:
                    frogs -= 1
                else:
                    cnt[i] += 1
        return ans if frogs == 0 and sum(cnt) == 0 else -1

    def minNumberOfFrogs_map(self, croakOfFrogs: str) -> int:
        """
        Interview explanation:
        Alternate with explicit prev-letter map and same concurrency tracking.

        Algorithm:
        - prev = {'r':'c','o':'r','a':'o','k':'a'}; counters dict.

        Complexity: O(n) time, O(1) space.
        """
        need = {"c": 0, "r": 0, "o": 0, "a": 0, "k": 0}
        prev = {"r": "c", "o": "r", "a": "o", "k": "a"}
        cur = ans = 0
        for ch in croakOfFrogs:
            if ch == "c":
                cur += 1
                ans = max(ans, cur)
                need["c"] += 1
            else:
                p = prev[ch]
                if need[p] == 0:
                    return -1
                need[p] -= 1
                if ch == "k":
                    cur -= 1
                else:
                    need[ch] += 1
        return -1 if cur or any(need.values()) else ans
# @lc code=end
