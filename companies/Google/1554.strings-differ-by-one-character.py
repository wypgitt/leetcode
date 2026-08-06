#
# @lc app=leetcode id=1554 lang=python3
#
# [1554] Strings Differ by One Character
#
# https://leetcode.com/problems/strings-differ-by-one-character/description/
#
# algorithms
# Medium (39.66%)
# Likes:    388
# Dislikes: 106
# Total Accepted:    28K
# Total Submissions: 70.6K
# Testcase Example:  "[\"abcd\",\"acbd\", \"aacd\"]"
#
#
# Given a list of strings dict where all the strings are of the same
# length.
#
# Return true if there are 2 strings that only differ by 1 character in
# the same index, otherwise return false.
#
# Example 1:
#
# Input: dict = ["abcd","acbd", "aacd"]
# Output: true
# Explanation: Strings "abcd" and "aacd" differ only by one character in
# the index 1.
#
# Example 2:
#
# Input: dict = ["ab","cd","yz"]
# Output: false
#
# Example 3:
#
# Input: dict = ["abcd","cccc","abyd","abab"]
# Output: true
#
# Constraints:
#
# The number of characters in dict <= 10^5
#
# dict[i].length == dict[j].length
#
# dict[i] should be unique.
#
# dict[i] contains only lowercase English letters.
#
# @lc code=start
from typing import List


class Solution:
    def differByOne(self, dict: List[str]) -> bool:
        """
        Interview explanation:
        Premium. Words same length; return true if two differ in exactly one
        position. Mask each index with '*' (or hash); collision on same mask
        means two words match everywhere else.

        Algorithm (wildcard mask set):
        - For each word, for each index i, form mask with word[:i]+'*'+word[i+1:].
        - If mask seen, return True; else add.
        - Careful: same mask from identical words shouldn't false-positive if
          dict has uniques; LeetCode guarantees distinct words.

        Complexity: O(N * L^2) time/space for string masks (L=word length).
        """
        seen = set()
        for w in dict:
            for i in range(len(w)):
                mask = w[:i] + "*" + w[i + 1 :]
                if mask in seen:
                    return True
                seen.add(mask)
        return False

    def differByOne_hash(self, dict: List[str]) -> bool:
        """
        Interview explanation:
        Alternate rolling-hash: store hash of each word; for each position,
        remove that char's contribution and check collisions in a set.

        Algorithm:
        - Base-26/prime hashes; for each i, put hash_without_i into set across words.

        Complexity: O(N*L) expected time, O(N) space.
        """
        if not dict:
            return False
        n, L = len(dict), len(dict[0])
        MOD = 10**18 + 3
        BASE = 911382323
        pows = [1] * (L + 1)
        for i in range(L):
            pows[i + 1] = (pows[i] * BASE) % MOD
        full = []
        for w in dict:
            h = 0
            for ch in w:
                h = (h * BASE + (ord(ch) - 96)) % MOD
            full.append(h)
        for i in range(L):
            buckets = {}
            p = pows[L - 1 - i]
            for idx, w in enumerate(dict):
                h = (full[idx] - (ord(w[i]) - 96) * p) % MOD
                if h in buckets and buckets[h] != w:
                    # verify exact one-diff (hash collision guard)
                    other = buckets[h]
                    diff = sum(a != b for a, b in zip(w, other))
                    if diff == 1:
                        return True
                buckets[h] = w
        return False
# @lc code=end

