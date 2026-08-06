#
# @lc app=leetcode id=1618 lang=python3
#
# [1618] Maximum Font to Fit a Sentence in a Screen
#
# https://leetcode.com/problems/maximum-font-to-fit-a-sentence-in-a-screen/description/
#
# algorithms
# Medium (61.85%)
# Likes:    114
# Dislikes: 22
# Total Accepted:    7.6K
# Total Submissions: 12.3K
# Testcase Example:  "\"helloworld\"\n80\n20\n[6,8,10,12,14,16,18,24,36]"
#
#
# You are given a string text. We want to display text on a screen of
# width w and height h. You can choose any font size from array fonts,
# which contains the available font sizes in ascending order.
#
#
#
# You can use the FontInfo interface to get the width and height of any
# character at any available font size.
#
#
#
# The FontInfo interface is defined as such:
#
#
#
#
# interface FontInfo {
#   // Returns the width of character ch on the screen using font size
# fontSize.
#   // O(1) per call
#   public int getWidth(int fontSize, char ch);
#
#   // Returns the height of any character on the screen using font size
# fontSize.
#   // O(1) per call
#   public int getHeight(int fontSize);
# }
#
#
#
# The calculated width of text for some fontSize is the sum of every
# getWidth(fontSize, text[i]) call for each 0 <= i < text.length
# (0-indexed). The calculated height of text for some fontSize is
# getHeight(fontSize). Note that text is displayed on a single line.
#
#
#
# It is guaranteed that FontInfo will return the same value if you call
# getHeight or getWidth with the same parameters.
#
#
#
# It is also guaranteed that for any font size fontSize and any character
# ch:
#
#
#
#
#
# getHeight(fontSize) <= getHeight(fontSize+1)
#
#
# getWidth(fontSize, ch) <= getWidth(fontSize+1, ch)
#
#
#
#
#
# Return the maximum font size you can use to display text on the screen.
# If text cannot fit on the display with any font size, return -1.
#
#
#
#
#
# Example 1:
#
#
#
#
# Input: text = "helloworld", w = 80, h = 20, fonts =
# [6,8,10,12,14,16,18,24,36]
# Output: 6
#
#
#
#
# Example 2:
#
#
#
#
# Input: text = "leetcode", w = 1000, h = 50, fonts = [1,2,4]
# Output: 4
#
#
#
#
# Example 3:
#
#
#
#
# Input: text = "easyquestion", w = 100, h = 100, fonts = [10,15,20,25]
# Output: -1
#
#
#
#
#
#
# Constraints:
#
#
#
#
#
# 1 <= text.length <= 50000
#
#
# text contains only lowercase English letters.
#
#
# 1 <= w <= 10^7
#
#
# 1 <= h <= 10^4
#
#
# 1 <= fonts.length <= 10^5
#
#
# 1 <= fonts[i] <= 10^5
#
#
# fonts is sorted in ascending order and does not contain duplicates.
#
# @lc code=start
from typing import List

# """
# This is FontInfo's API interface.
# You should not implement it, or speculate about its implementation
# """
# class FontInfo(object):
#    def getWidth(self, fontSize: int, ch: str) -> int:
#        pass
#    def getHeight(self, fontSize: int) -> int:
#        pass

try:
    FontInfo  # type: ignore[name-defined]
except NameError:

    class FontInfo:  # type: ignore[no-redef]
        def getWidth(self, fontSize: int, ch: str) -> int:
            return 0

        def getHeight(self, fontSize: int) -> int:
            return 0


class Solution:
    def maxFont(
        self, text: str, w: int, h: int, fonts: List[int], fontInfo: "FontInfo"
    ) -> int:
        """
        Interview explanation:
        Premium. fonts is sorted ascending. Largest fontSize that fits text in
        w x h using FontInfo.getWidth/getHeight. Binary search fonts.

        Algorithm (binary search):
        - Check(mid): height<=h and sum(getWidth(font,ch))<=w.
        - Binary search rightmost fitting font in fonts; else -1.

        Complexity: O(log F * |text|) time.
        """
        def fits(fs: int) -> bool:
            if fontInfo.getHeight(fs) > h:
                return False
            width = 0
            for ch in text:
                width += fontInfo.getWidth(fs, ch)
                if width > w:
                    return False
            return True

        lo, hi = 0, len(fonts) - 1
        ans = -1
        while lo <= hi:
            mid = (lo + hi) // 2
            if fits(fonts[mid]):
                ans = fonts[mid]
                lo = mid + 1
            else:
                hi = mid - 1
        return ans

    def maxFont_linear(
        self, text: str, w: int, h: int, fonts: List[int], fontInfo: "FontInfo"
    ) -> int:
        """
        Interview explanation:
        Alternate linear scan from largest font downward (fonts sorted).

        Algorithm:
        - For fs in reversed(fonts): if fits return fs; return -1.

        Complexity: O(F * |text|) time.
        """
        def fits(fs: int) -> bool:
            if fontInfo.getHeight(fs) > h:
                return False
            return sum(fontInfo.getWidth(fs, ch) for ch in text) <= w

        for fs in reversed(fonts):
            if fits(fs):
                return fs
        return -1
# @lc code=end
