#
# @lc app=leetcode id=391 lang=python3
#
# [391] Perfect Rectangle
#
# https://leetcode.com/problems/perfect-rectangle/description/
#
# algorithms
# Hard (37.89%)
# Likes:    958
# Dislikes: 120
# Total Accepted:    61.5K
# Total Submissions: 162.3K
# Testcase Example:  '[[1,1,3,3],[3,1,4,2],[3,2,4,4],[1,3,2,4],[2,3,3,4]]'
#
# Given an array rectangles where rectangles[i] = [xi, yi, ai, bi] represents
# an axis-aligned rectangle. The bottom-left point of the rectangle is (xi, yi)
# and the top-right point of it is (ai, bi).
# 
# Return true if all the rectangles together form an exact cover of a
# rectangular region.
# 
# 
# Example 1:
# 
# 
# Input: rectangles = [[1,1,3,3],[3,1,4,2],[3,2,4,4],[1,3,2,4],[2,3,3,4]]
# Output: true
# Explanation: All 5 rectangles together form an exact cover of a rectangular
# region.
# 
# 
# Example 2:
# 
# 
# Input: rectangles = [[1,1,2,3],[1,3,2,4],[3,1,4,2],[3,2,4,4]]
# Output: false
# Explanation: Because there is a gap between the two rectangular regions.
# 
# 
# Example 3:
# 
# 
# Input: rectangles = [[1,1,3,3],[3,1,4,2],[1,3,2,4],[2,2,4,4]]
# Output: false
# Explanation: Because two of the rectangles overlap with each other.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= rectangles.length <= 2 * 10^4
# rectangles[i].length == 4
# -10^5 <= xi < ai <= 10^5
# -10^5 <= yi < bi <= 10^5
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def isRectangleCover(self, rectangles: List[List[int]]) -> bool:
        """
        Interview explanation
        =====================

        Restate the problem
        -------------------
        We are given many axis-aligned rectangles.  Each rectangle is represented
        as:

            [x1, y1, x2, y2]

        where `(x1, y1)` is the bottom-left corner and `(x2, y2)` is the
        top-right corner.

        We need decide whether all rectangles together form one exact rectangular
        cover:

        * no gaps
        * no overlaps
        * the union is exactly one larger axis-aligned rectangle

        Key idea
        --------
        A perfect rectangle cover has two necessary and sufficient properties:

        1. The sum of all small rectangle areas equals the area of the outer
           bounding rectangle.

        2. After toggling every small rectangle corner, exactly four corners
           remain:

               bottom-left of the bounding rectangle
               bottom-right of the bounding rectangle
               top-left of the bounding rectangle
               top-right of the bounding rectangle

        Why corner toggling works
        -------------------------
        In a perfect cover, every corner that lies inside the final rectangle is
        shared by rectangles in pairs or groups.  Such internal corners appear an
        even number of times when we list all small-rectangle corners.

        If we add a corner to a set when first seen and remove it when seen
        again, every even-count internal corner disappears.

        The only corners that appear odd times are the four outside corners of
        the final rectangle.

        Why area is also needed
        -----------------------
        Corner parity alone is not enough.  It mainly checks the boundary and
        local corner consistency.  Area ensures there is no hidden overlap/gap
        combination that preserves the same four outer corners.

        The two checks together are powerful:

        * If there is a gap, the total area is too small, or extra unmatched
          corners appear around the gap.
        * If there is an overlap, the total area is too large, or corner parity
          is disturbed.
        * If pieces form multiple regions, the corner set will not match exactly
          the four corners of one bounding rectangle unless area also fails.

        Algorithm
        ---------
        1. Track the bounding rectangle:

               min_x, min_y, max_x, max_y

        2. Accumulate `total_area` of all input rectangles.
        3. Maintain a set `corners`.
           For every rectangle, toggle its four corners:

               if corner is in set: remove it
               otherwise: add it

        4. Compute the bounding rectangle area:

               bounding_area = (max_x - min_x) * (max_y - min_y)

        5. The cover is perfect if and only if:

               total_area == bounding_area

           and:

               corners == {
                   (min_x, min_y),
                   (min_x, max_y),
                   (max_x, min_y),
                   (max_x, max_y)
               }

        Data structure choice
        ---------------------
        We use a set of coordinate tuples.

        Why a set?

        * corner toggling needs O(1) average insert/delete/lookup
        * tuple coordinates are hashable
        * at the end, the set should contain exactly four points

        No sweep line or interval tree is needed.  The area-plus-corner invariant
        solves the exact-cover decision directly.

        Correctness proof
        -----------------
        Lemma 1: If the rectangles form a perfect cover, the final corner set is
        exactly the four bounding rectangle corners.
        In a perfect cover, any non-boundary corner is shared by adjacent
        rectangles and appears an even number of times, so toggling removes it.
        Any point on a straight boundary but not an outer corner also appears an
        even number of times.  The four extreme outer corners each appear once,
        so exactly those four remain.

        Lemma 2: If the rectangles form a perfect cover, total area equals the
        bounding rectangle area.
        A perfect cover partitions the bounding rectangle without overlap or
        gaps.  Therefore the sum of all piece areas is exactly the area of the
        bounding rectangle.

        Lemma 3: If the final corner set is exactly the four bounding corners
        and total area equals bounding area, then the rectangles form a perfect
        cover.
        The matching corner set rules out extra exposed boundary corners and
        inconsistent internal corner structure.  The area equality rules out
        missing area and extra overlapped area inside the bounding rectangle.
        Together, these conditions force the union of rectangles to occupy
        exactly the bounding rectangle once.

        Theorem: The algorithm returns True if and only if the rectangles form a
        perfect rectangular cover.
        If they form a perfect cover, Lemma 1 and Lemma 2 show both algorithm
        checks pass.  If both checks pass, Lemma 3 shows the rectangles form a
        perfect cover.  Therefore the algorithm is correct.

        Complexity analysis
        -------------------
        Let n = len(rectangles).

        We process each rectangle once and toggle four corners.

        Total time:  O(n)
        Total space: O(n)

        The corner set can temporarily contain O(n) distinct points.

        Edge cases
        ----------
        * Single rectangle:
          Its four corners are the bounding corners and areas match, so True.

        * Gap:
          Area is too small or extra corners remain.

        * Overlap:
          Area is too large or corner parity fails.

        * Negative coordinates:
          Area differences and tuple corners work normally.

        * Rectangles only touch at edges/corners:
          Touching is allowed as long as the union is one perfect rectangle.

        Test strategy
        -------------
        Useful tests:

        * Provided examples:
              exact cover -> True
              gap         -> False
              overlap     -> False

        * Single rectangle.
        * Rectangles with negative coordinates.
        * Cover split into strips.
        * Same bounding box but with both a gap and overlap.

        Possible improvement?
        ---------------------
        A sweep-line algorithm can also detect overlaps and gaps, but it is more
        complex and typically O(n log n).  The area-plus-corner method is the
        cleanest solution here: linear time, simple state, and directly tailored
        to exact rectangle cover.
        """

        min_x = float("inf")
        min_y = float("inf")
        max_x = float("-inf")
        max_y = float("-inf")
        total_area = 0
        corners: set[tuple[int, int]] = set()

        def toggle(point: tuple[int, int]) -> None:
            if point in corners:
                corners.remove(point)
            else:
                corners.add(point)

        for x1, y1, x2, y2 in rectangles:
            min_x = min(min_x, x1)
            min_y = min(min_y, y1)
            max_x = max(max_x, x2)
            max_y = max(max_y, y2)

            total_area += (x2 - x1) * (y2 - y1)

            toggle((x1, y1))
            toggle((x1, y2))
            toggle((x2, y1))
            toggle((x2, y2))

        bounding_corners = {
            (min_x, min_y),
            (min_x, max_y),
            (max_x, min_y),
            (max_x, max_y),
        }
        bounding_area = (max_x - min_x) * (max_y - min_y)

        return total_area == bounding_area and corners == bounding_corners
# @lc code=end
