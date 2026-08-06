#
# @lc app=leetcode id=3582 lang=python3
#
# [3582] Generate Tag for Video Caption
#
# https://leetcode.com/problems/generate-tag-for-video-caption/description/
#
# algorithms
# Easy (32.64%)
# Likes:    74
# Dislikes: 30
# Total Accepted:    44.9K
# Total Submissions: 137.7K
# Testcase Example:  "\"Leetcode daily streak achieved\""
#
#
# You are given a string caption representing the caption for a video.
#
# The following actions must be performed in order to generate a valid tag
# for the video:
#
# Combine all words in the string into a single camelCase string prefixed
# with '#'. A camelCase string is one where the first letter of all words
# except the first one is capitalized. All characters after the first
# character in each word must be lowercase.
#
# Remove all characters that are not an English letter, except the first
# '#'.
#
# Truncate the result to a maximum of 100 characters.
#
# Return the tag after performing the actions on caption.
#
# Example 1:
#
# Input: caption = "Leetcode daily streak achieved"
#
# Output: "#leetcodeDailyStreakAchieved"
#
# Explanation:
#
# The first letter for all words except "leetcode" should be capitalized.
#
# Example 2:
#
# Input: caption = "can I Go There"
#
# Output: "#canIGoThere"
#
# Explanation:
#
# The first letter for all words except "can" should be capitalized.
#
# Example 3:
#
# Input: caption =
# "hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh"
#
# Output:
# "#hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh"
#
# Explanation:
#
# Since the first word has length 101, we need to truncate the last two
# letters from the word.
#
# Constraints:
#
# 1 <= caption.length <= 150
#
# caption consists only of English letters and ' '.
#

# @lc code=start

class Solution:
    def generateTag(self, caption: str) -> str:
        """
        Interview explanation:
        Build a camelCase hashtag from caption words, then truncate to 100 chars.

        Algorithm:
        - Split on spaces; lowercase the first word; Capitalize later words.
        - Prefix '#', keep only letters via the word transform, slice to 100.

        Complexity: O(n) time, O(n) space.
        """
        parts = caption.split()
        if not parts:
            return "#"
        body = parts[0].lower() + "".join(
            w[:1].upper() + w[1:].lower() for w in parts[1:]
        )
        return ("#" + body)[:100]

    def generateTag_scan(self, caption: str) -> str:
        """
        Interview explanation:
        Alternate: single scan, capitalize after spaces, force first letter lower.

        Algorithm:
        - Append letters with case rules; stop at length 100; lowercase index 1.

        Complexity: O(n) time, O(n) space.
        """
        out = ["#"]
        for i, ch in enumerate(caption):
            if ch == " ":
                continue
            if i == 0 or caption[i - 1] == " ":
                out.append(ch.upper())
            else:
                out.append(ch.lower())
            if len(out) == 100:
                break
        if len(out) > 1:
            out[1] = out[1].lower()
        return "".join(out)
# @lc code=end
