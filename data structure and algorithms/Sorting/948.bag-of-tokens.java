/*
 * @lc app=leetcode id=948 lang=java
 *
 * [948] Bag Of Tokens
 */

/*
 * --- Interview notes (greedy two pointers, exchange argument, complexity) ---
 *
 * Problem
 * Maximize score: face-up pays tokens[i] power and gains score; face-down requires score>=1, gains tokens[j] power, loses 1 score.
 * Track peak score during optimal play.
 *
 * Greedy: sort ascending. lo=cheapest, hi=most expensive. If power >= tokens[lo], buy cheapest face-up; else if score>0, sell most expensive face-down; else stop.
 *
 * Time O(n log n), Space O(1) auxiliary.
 *
 * --- end notes ---
 */

import java.util.Arrays;

// @lc code=start
class Solution {
    public int bagOfTokensScore(int[] tokens, int power) {
        Arrays.sort(tokens);
        int lo = 0;
        int hi = tokens.length - 1;
        int score = 0;
        int best = 0;
        while (lo <= hi) {
            if (power >= tokens[lo]) {
                power -= tokens[lo++];
                score++;
                if (score > best) {
                    best = score;
                }
            } else if (score > 0) {
                power += tokens[hi--];
                score--;
            } else {
                break;
            }
        }
        return best;
    }
}
// @lc code=end
