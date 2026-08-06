#
# @lc app=leetcode id=2325 lang=python3
#
# [2325] Decode the Message
#
# https://leetcode.com/problems/decode-the-message/description/
#
# algorithms
# Easy (85.92%)
# Likes:    1146
# Dislikes: 114
# Total Accepted:    159.6K
# Total Submissions: 185.7K
# Testcase Example:  "\"the quick brown fox jumps over the lazy dog\"\n\"vkbs bs t suepuv\""
#
# You are given the strings key and message, which represent a cipher key and a
# secret message, respectively. The steps to decode message are as follows:
#
#
# Use the first appearance of all 26 lowercase English letters in key as the
# order of the substitution table.
#
#
# Align the substitution table with the regular English alphabet.
#
#
# Each letter in message is then substituted using the table.
#
#
# Spaces ' ' are transformed to themselves.
#
#
# For example, given key = "happy boy" (actual key would have at least one
# instance of each letter in the alphabet), we have the partial substitution
# table of ('h' -> 'a', 'a' -> 'b', 'p' -> 'c', 'y' -> 'd', 'b' -> 'e', 'o' ->
# 'f').
#
# Return the decoded message.
#
#
#
# Example 1:
#
# Input: key = "the quick brown fox jumps over the lazy dog", message = "vkbs bs
# t suepuv"
# Output: "this is a secret"
# Explanation: The diagram above shows the substitution table.
# It is obtained by taking the first appearance of each letter in "the quick
# brown fox jumps over the lazy dog".
#
# Example 2:
#
# Input: key = "eljuxhpwnyrdgtqkviszcfmabo", message = "zwx hnfx lqantp mnoeius
# ycgk vcnjrdb"
# Output: "the five boxing wizards jump quickly"
# Explanation: The diagram above shows the substitution table.
# It is obtained by taking the first appearance of each letter in
# "eljuxhpwnyrdgtqkviszcfmabo".
#
#
#
# Constraints:
#
#
# 26 <= key.length <= 2000
#
#
# key consists of lowercase English letters and ' '.
#
#
# key contains every letter in the English alphabet ('a' to 'z') at least once.
#
#
# 1 <= message.length <= 2000
#
#
# message consists of lowercase English letters and ' '.
#

# @lc code=start
class Solution:
    def decodeMessage(self, key: str, message: str) -> str:
        """
        Interview explanation:
        Substitution cipher: first occurrence of letters in `key` map to a..z
        in order; decode `message` (spaces unchanged).

        Algorithm:
        - Build map from key letters (skip spaces/dupes); translate message.

        Complexity: O(|key| + |message|) time, O(1) space.
        """
        mp = {}
        for ch in key:
            if ch != ' ' and ch not in mp:
                mp[ch] = chr(ord('a') + len(mp))
                if len(mp) == 26:
                    break
        return ''.join(ch if ch == ' ' else mp[ch] for ch in message)
# @lc code=end
