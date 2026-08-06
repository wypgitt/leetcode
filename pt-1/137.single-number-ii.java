/*
 * @lc app=leetcode id=137 lang=java
 *
 * [137] Single Number II
 */

/*
 * =============================================================================
 * INTERVIEW: HOW TO EXPLAIN (elevator → whiteboard)
 * =============================================================================
 *
 * 30 seconds:
 *   "Every number except one appears three times. Count each bit position across
 *   all numbers: if the total count of 1s is not divisible by 3, that bit is
 *   set in the unique answer. Rebuild the integer from those bits."
 *
 * 2–4 minutes — two standard angles:
 *
 *   (A) Bit-count / modulo 3 (usually easiest to derive live):
 *       - For bit position i, each triple contributes either 0 or 3 to the sum
 *         of bits; the singleton contributes 0 or 1. So (sum of bits at i) % 3
 *         equals the i-th bit of the answer.
 *       - Do this for i = 0..31, OR the bits into `ans`.
 *       - At the end, interpret `ans` as a signed 32-bit int for languages /
 *         Python big-int quirks (see EDGE CASES).
 *
 *   (B) "Digital logic" / state machine (one pass, same complexity):
 *       - For each bit position, count occurrences mod 3 using two masks:
 *         `once` = bits seen 1 mod 3 times; `twice` = bits seen 2 mod 3 times.
 *       - Update rules (derived from truth table or small FSM):
 *             once = (once ^ x) & ~twice
 *             twice = (twice ^ x) & ~once
 *       - After all numbers, `once` holds the unique value; `twice` is 0.
 *
 * =============================================================================
 * ALGORITHM (implemented below: approach B)
 * =============================================================================
 *
 * We maintain two integers `once` and `twice` such that, independently for
 * every bit index, the pair encodes count(x) mod 3 for that bit as we stream
 * through `nums`:
 *   count ≡ 0 (mod 3) → bit off in both once and twice
 *   count ≡ 1 (mod 3) → bit on in once only
 *   count ≡ 2 (mod 3) → bit on in twice only
 *
 * Processing `x`, the updates XOR in the new number (toggle) but AND with a
 * complement mask clears transitions that would violate the mod-3 discipline.
 * This is equivalent to a tiny 3-state FSM per bit, SIMD-packed into ints.
 *
 * Why XOR: toggles presence of a bit; combined with & ~other mask it enforces
 * "third occurrence resets to zero," matching triple-cancel behavior.
 *
 * =============================================================================
 * DATA STRUCTURES
 * =============================================================================
 *
 * - nums: input array (read-only).
 * - once, twice: two integers acting as parallel bit vectors (no auxiliary
 *   arrays). Space O(1) beyond input.
 *
 * Alternative (approach A): no extra state beyond an accumulator `ans`; inner
 * loop counts bits — still O(1) extra space, O(32 · n) time.
 *
 * =============================================================================
 * COMPLEXITY
 * =============================================================================
 *
 * Time:  O(n) — single pass over nums; bitwise ops are O(1) per element.
 * Space: O(1) — two integer registers (32-bit).
 *
 * Approach A is O(32 · n) time, still O(n) asymptotically; often easier to code
 * under pressure.
 *
 * =============================================================================
 * EDGE CASES
 * =============================================================================
 *
 * - n == 1: loop runs once; `once == nums[0]`, return it.
 * - All duplicates except one: guaranteed by problem statement.
 * - Negative values / 32-bit range: LeetCode uses signed 32-bit values.
 * - Overflow: not an issue for 32-bit constraints when using int32 reasoning.
 *
 * =============================================================================
 * TESTING
 * =============================================================================
 *
 * Unit tests:
 *   - Minimal: [2,2,2,3] → 3
 *   - With zero: [0,0,0,5] → 5
 * Stress: Random valid arrays vs frequency-mod-3 reference.
 *
 * =============================================================================
 */

// @lc code=start
class Solution {
    /**
     * Every element appears three times except one element appears once.
     *
     * <p>Implementation: two-mask finite-state machine. {@code once} collects bits whose cumulative count mod 3 is 1 —
     * that is the unique number after processing all inputs.
     */
    public int singleNumber(int[] nums) {
        int once = 0;
        int twice = 0;
        for (int x : nums) {
            once = (once ^ x) & ~twice;
            twice = (twice ^ x) & ~once;
        }
        return once;
    }
}
// @lc code=end
