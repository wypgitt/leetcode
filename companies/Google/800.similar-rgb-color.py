#
# @lc app=leetcode id=800 lang=python3
#
# [800] Similar RGB Color
#
# https://leetcode.com/problems/similar-rgb-color/description/
#
# algorithms
# Easy (67.97%)
# Likes:    112
# Dislikes: 692
# Total Accepted:    18.7K
# Total Submissions: 27.4K
# Testcase Example:  "\"#09f166\""
#
#
# The red-green-blue color "#AABBCC" can be written as "#ABC" in
# shorthand.
#
# For example, "#15c" is shorthand for the color "#1155cc".
#
# The similarity between the two colors "#ABCDEF" and "#UVWXYZ" is -(AB -
# UV)^2 - (CD - WX)^2 - (EF - YZ)^2.
#
# Given a string color that follows the format "#ABCDEF", return a string
# represents the color that is most similar to the given color and has a
# shorthand (i.e., it can be represented as some "#XYZ").
#
# Any answer which has the same highest similarity as the best answer will
# be accepted.
#
# Example 1:
#
# Input: color = "#09f166"
# Output: "#11ee66"
# Explanation:
# The similarity is -(0x09 - 0x11)^2 -(0xf1 - 0xee)^2 - (0x66 - 0x66)^2 =
# -64 -9 -0 = -73.
# This is the highest among any shorthand color.
#
# Example 2:
#
# Input: color = "#4e3fe1"
# Output: "#5544dd"
#
# Constraints:
#
# color.length == 7
#
# color[0] == '#'
#
# color[i] is either digit or character in the range ['a', 'f'] for i > 0.
#
# @lc code=start
class Solution:
    def similarRGB(self, color: str) -> str:
        """
        Interview explanation:
        Premium. Shorthand RGB is #xyxyxy form (each channel two identical hex
        digits). Find shorthand minimizing squared Euclidean distance in RGB.
        For each channel byte, round to nearest 0x00,0x11,...,0xff
        (i.e. nearest multiple of 17).

        Algorithm:
        - For each pair of hex digits (R,G,B):
          v = int(pair, 16); nearest = round(v / 17) * 17 (clamp 0..15).
          append f"{nearest//17:x}"*2
        - Return "#" + joined.

        Complexity: O(1) time/space.
        """
        def nearest(comp: str) -> str:
            v = int(comp, 16)
            # candidates are 0, 17, 34, ..., 255
            q = round(v / 17)
            q = max(0, min(15, q))
            return format(q, "x") * 2

        return "#" + nearest(color[1:3]) + nearest(color[3:5]) + nearest(color[5:7])
# @lc code=end

