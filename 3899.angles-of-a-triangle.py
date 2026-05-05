#
# @lc app=leetcode id=3899 lang=python3
#
# [3899] Angles of a Triangle
#
# https://leetcode.com/problems/angles-of-a-triangle/description/
#
# algorithms
# Medium (62.00%)
# Likes:    32
# Dislikes: 36
# Total Accepted:    32.8K
# Total Submissions: 52.9K
# Testcase Example:  '[3,4,5]'
#
# You are given a positive integer array sides of length 3.
# 
# Determine if there exists a triangle with positive area whose three side
# lengths are given by the elements of sides.
# 
# If such a triangle exists, return an array of three floating-point numbers
# representing its internal angles (in degrees), sorted in non-decreasing
# order. Otherwise, return an empty array.
# 
# Answers within 10^-5 of the actual answer will be accepted.
# 
# 
# Example 1:
# 
# 
# Input: sides = [3,4,5]
# 
# Output: [36.86990,53.13010,90.00000]
# 
# Explanation:
# 
# You can form a right-angled triangle with side lengths 3, 4, and 5. The
# internal angles of this triangle are approximately 36.869897646,
# 53.130102354, and 90 degrees respectively.
# 
# 
# Example 2:
# 
# 
# Input: sides = [2,4,2]
# 
# Output: []
# 
# Explanation:
# 
# You cannot form a triangle with positive area using side lengths 2, 4, and
# 2.
# 
# 
# 
# Constraints:
# 
# 
# sides.length == 3
# 1 <= sides[i] <= 1000
# 
# 
#

# @lc code=start
class Solution:
    def internalAngles(self, sides: list[int]) -> list[float]:
        """
        Problem: Angles of a Triangle
        Difficulty: Medium
        
        Problem Description:
        Given three positive integers representing side lengths of a potential triangle,
        determine if they can form a triangle with positive area. If yes, return the
        three internal angles in degrees, sorted in non-decreasing order. If not,
        return an empty list.
        
        Algorithm Explanation:
        1. Triangle Inequality Check: For three sides a, b, c to form a triangle,
           they must satisfy a + b > c, a + c > b, and b + c > a. This ensures
           positive area and prevents degenerate cases (e.g., collinear points).
           Why? Because if any inequality fails, the sides cannot enclose a space.
        
        2. Angle Calculation: Use the Law of Cosines for each angle.
           - Law of Cosines: For angle C opposite side c: cos(C) = (a² + b² - c²) / (2ab)
           - Compute cosine, then use inverse cosine (acos) to get angle in radians,
             then convert to degrees.
           - Repeat for all three angles.
           Why Law of Cosines? It's the standard formula for angles in a triangle
           when all sides are known. More efficient than Law of Sines here since
           we have all sides.
        
        3. Sorting: Sort the angles in non-decreasing order as required.
        
        Why this Algorithm?
        - Straightforward and directly addresses the problem requirements.
        - No need for complex data structures; simple arithmetic operations suffice.
        - Accurate for the given constraints (sides up to 1000, so no precision issues
          beyond the 10^-5 tolerance).
        
        Data Structure Used:
        - Input: List of 3 integers (sides).
        - Output: List of 3 floats (angles) or empty list.
        - No additional data structures needed; we use built-in Python lists and math functions.
        - Why lists? Simple, efficient for small fixed-size data. No need for arrays or
          advanced structures since n=3.
        
        Time Complexity Analysis:
        - Triangle check: O(1) - constant comparisons.
        - Angle calculations: O(1) - fixed number of arithmetic operations and math calls.
        - Sorting: O(1) - sorting 3 elements is constant time.
        - Overall: O(1) - The problem size is fixed (3 sides), so time is constant
          regardless of input values.
        
        Space Complexity Analysis:
        - Input list: O(1) space (fixed size).
        - Local variables: O(1) - a few floats and the output list.
        - No additional space allocation beyond constants.
        - Overall: O(1) - Constant space usage.
        
        Edge Cases Considered:
        1. Valid Equilateral Triangle: [3,3,3] -> Angles [60.0, 60.0, 60.0]
           - All sides equal, all angles equal.
        2. Valid Right Triangle: [3,4,5] -> Angles [36.87, 53.13, 90.0]
           - One right angle, as in the example.
        3. Valid Isosceles Triangle: [2,2,3] -> Angles [~38.21, ~38.21, ~103.58]
           - Two sides equal, two angles equal.
        4. Invalid Triangle (fails inequality): [2,4,2] -> []
           - As in example 2.
        5. Invalid Triangle (another case): [1,1,3] -> []
           - Sum of two smaller sides equals the largest.
        6. Minimum Valid: [1,1,1] -> [60.0, 60.0, 60.0]
           - Smallest possible triangle.
        7. Large Sides: [1000,1000,1000] -> [60.0, 60.0, 60.0]
           - No overflow issues with int/float in Python.
        8. Floating Point Precision: Angles within 10^-5 tolerance, so math.acos
           and degrees should be fine for sides <= 1000.
        
        Test Cases (from problem and additional):
        - Example 1: [3,4,5] -> [36.86989764584402, 53.13010235415598, 90.0]
        - Example 2: [2,4,2] -> []
        - Additional: [1,1,1] -> [60.0, 60.0, 60.0]
        - Additional: [5,5,5] -> [60.0, 60.0, 60.0]
        - Additional: [1,2,3] -> [] (1+2=3, not >3)
        
        How to Explain in Interview:
        - Start with problem understanding: "We need to check if three sides form a triangle and compute angles."
        - Explain triangle inequality: "To form a triangle, each pair of sides must sum greater than the third."
        - Describe Law of Cosines: "For each angle, use cos = (a²+b²-c²)/(2ab), then acos and convert to degrees."
        - Discuss why: "This gives exact angles for the triangle."
        - Time/Space: "O(1) time and space since fixed operations."
        - Edge cases: "Handle invalid triangles by returning empty list, and ensure angles are sorted."
        - Improvements: "None needed; optimal for this problem. Could add input validation if sides not guaranteed positive."
        
        Potential Improvements:
        - Input Validation: Although constraints say 1 <= sides[i], in real code, check for positive integers.
        - Precision: Use higher precision if needed, but Python's float is sufficient here.
        - Code Readability: Could use a helper function for angle calculation to reduce repetition.
        - But for this problem, the simple implementation is fine.
        
        Implementation Notes:
        - Import math at the top or inside function; here inside for clarity.
        - Use sorted() or list.sort() for angles.
        - Ensure angles are floats as required.
        """
        import math
        
        a, b, c = sides
        
        # Step 1: Check triangle inequality
        if a + b <= c or a + c <= b or b + c <= a:
            return []
        
        # Step 2: Compute angles using Law of Cosines
        # Angle opposite to a
        cos_A = (b**2 + c**2 - a**2) / (2 * b * c)
        A = math.degrees(math.acos(cos_A))
        
        # Angle opposite to b
        cos_B = (a**2 + c**2 - b**2) / (2 * a * c)
        B = math.degrees(math.acos(cos_B))
        
        # Angle opposite to c
        cos_C = (a**2 + b**2 - c**2) / (2 * a * b)
        C = math.degrees(math.acos(cos_C))
        
        # Step 3: Collect and sort angles
        angles = [A, B, C]
        angles.sort()
        
        return angles
# @lc code=end

