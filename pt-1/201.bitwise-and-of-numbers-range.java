/*
 * @lc app=leetcode id=201 lang=java
 *
 * [201] Bitwise AND of Numbers Range
 */

/*
 * =============================================================================
 * PROBLEM (precise)
 * =============================================================================
 *
 * Given integers left <= right, compute bitwise AND of every integer in [left, right].
 *
 * =============================================================================
 * WHY NAIVE FAILS
 * =============================================================================
 *
 * Iterating x from left to right and updating ans &= x is correct but takes
 * O(right - left) time — unacceptable when the interval spans billions.
 *
 * We need O(log U) time using binary representation — no auxiliary arrays.
 *
 * =============================================================================
 * KEY OBSERVATION (common prefix / stripping unstable suffix bits)
 * =============================================================================
 *
 * Bits where left and right disagree at position k: enumerating all integers from
 * left to right forces that bit to be 0 in the AND. The answer is the shared
 * binary prefix of left and right — clear every bit to the right of the MSB
 * where left and right differ.
 *
 * =============================================================================
 * ALGORITHM A (implemented): right-shift until equal
 * =============================================================================
 *
 * Repeat: left >>= 1; right >>= 1; shift++ until left == right.
 * Then return left << shift.
 *
 * Time: O(log right). Space: O(1).
 *
 * =============================================================================
 * ALGORITHM B (alternative): while left < right: right &= right - 1; return right;
 *
 * =============================================================================
 * EDGE CASES
 * =============================================================================
 *
 * - left == right: AND of one number is that number.
 * - left = 0: valid.
 * - Use long if needed for shifts on edge constraints (Java int usually suffices for LC).
 *
 * =============================================================================
 */

// @lc code=start
class Solution {
    public int rangeBitwiseAnd(int left, int right) {
        int shift = 0;
        while (left != right) {
            left >>>= 1;
            right >>>= 1;
            shift++;
        }
        return left << shift;
    }
}
// @lc code=end
