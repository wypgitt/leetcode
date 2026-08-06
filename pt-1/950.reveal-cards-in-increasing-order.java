/*
 * @lc app=leetcode id=950 lang=java
 *
 * [950] Reveal Cards In Increasing Order
 */

/*
 * --- Interview notes (process simulation, deque, inverse assignment, complexity) ---
 *
 * Sort deck; assign smallest card to first revelation position, simulate reveal+move-next-to-bottom on unfilled slot indices using deque.
 *
 * Time O(n log n), Space O(n).
 *
 * --- end notes ---
 */

import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.Deque;

// @lc code=start
class Solution {
    public int[] deckRevealedIncreasing(int[] deck) {
        int[] cards = Arrays.copyOf(deck, deck.length);
        Arrays.sort(cards);
        int n = cards.length;
        Deque<Integer> dq = new ArrayDeque<>();
        for (int i = 0; i < n; i++) {
            dq.addLast(i);
        }
        int[] ans = new int[n];
        for (int x : cards) {
            ans[dq.pollFirst()] = x;
            if (!dq.isEmpty()) {
                dq.addLast(dq.pollFirst());
            }
        }
        return ans;
    }
}
// @lc code=end
