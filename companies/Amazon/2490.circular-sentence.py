#
# @lc app=leetcode id=2490 lang=python3
#
# [2490] Circular Sentence
#
# https://leetcode.com/problems/circular-sentence/description/
#
# algorithms
# Easy (70.07%)
# Likes:    769
# Dislikes: 28
# Total Accepted:    193.2K
# Total Submissions: 275.7K
# Testcase Example:  "\"leetcode exercises sound delightful\""
#
# A sentence is a list of words that are separated by a single space with no
# leading or trailing spaces.
#
#
# For example, "Hello World", "HELLO", "hello world hello world" are all
# sentences.
#
# Words consist of only uppercase and lowercase English letters. Uppercase and
# lowercase English letters are considered different.
#
# A sentence is circular if:
#
#
# The last character of each word in the sentence is equal to the first
# character of its next word.
#
#
# The last character of the last word is equal to the first character of the
# first word.
#
# For example, "leetcode exercises sound delightful", "eetcode", "leetcode eats
# soul" are all circular sentences. However, "Leetcode is cool", "happy
# Leetcode", "Leetcode" and "I like Leetcode" are not circular sentences.
#
# Given a string sentence, return true if it is circular. Otherwise, return
# false.
#
#
#
# Example 1:
#
# Input: sentence = "leetcode exercises sound delightful"
# Output: true
# Explanation: The words in sentence are ["leetcode", "exercises", "sound",
# "delightful"].
# - leetcode's last character is equal to exercises's first character.
# - exercises's last character is equal to sound's first character.
# - sound's last character is equal to delightful's first character.
# - delightful's last character is equal to leetcode's first character.
# The sentence is circular.
#
# Example 2:
#
# Input: sentence = "eetcode"
# Output: true
# Explanation: The words in sentence are ["eetcode"].
# - eetcode's last character is equal to eetcode's first character.
# The sentence is circular.
#
# Example 3:
#
# Input: sentence = "Leetcode is cool"
# Output: false
# Explanation: The words in sentence are ["Leetcode", "is", "cool"].
# - Leetcode's last character is not equal to is's first character.
# The sentence is not circular.
#
#
#
# Constraints:
#
#
# 1 <= sentence.length <= 500
#
#
# sentence consist of only lowercase and uppercase English letters and spaces.
#
#
# The words in sentence are separated by a single space.
#
#
# There are no leading or trailing spaces.
#

# @lc code=start
class Solution:
    def isCircularSentence(self, sentence: str) -> bool:
        """
        Interview explanation:
        Sentence is circular if each word's last char equals next word's first,
        and last word's last equals first word's first.

        Algorithm:
        - Split; check adjacent ends/starts and wrap-around.

        Complexity: O(n) time, O(n) space.
        """
        w = sentence.split()
        for i in range(len(w)):
            if w[i][-1] != w[(i + 1) % len(w)][0]:
                return False
        return True

    def isCircularSentence_scan(self, sentence: str) -> bool:
        """
        Interview explanation:
        Alternate single scan without splitting into a list copy of words.

        Algorithm:
        - Check sentence[0]==sentence[-1]; at each space, chars around it match.

        Complexity: O(n) time, O(1) space.
        """
        if sentence[0] != sentence[-1]:
            return False
        for i, ch in enumerate(sentence):
            if ch == " " and sentence[i - 1] != sentence[i + 1]:
                return False
        return True
# @lc code=end

