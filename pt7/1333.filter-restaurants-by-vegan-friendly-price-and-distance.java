import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/*
 * LeetCode 1333 - Filter Restaurants by Vegan-Friendly, Price and Distance
 */
class Solution {
    public List<Integer> filterRestaurants(
            int[][] restaurants,
            int veganFriendly,
            int maxPrice,
            int maxDistance) {

        List<int[]> filtered = new ArrayList<>();

        for (int[] restaurant : restaurants) {
            int id = restaurant[0];
            int rating = restaurant[1];
            int vegan = restaurant[2];
            int price = restaurant[3];
            int distance = restaurant[4];

            if (veganFriendly == 1 && vegan == 0) {
                continue;
            }
            if (price > maxPrice || distance > maxDistance) {
                continue;
            }

            filtered.add(new int[] {rating, id});
        }

        Collections.sort(filtered, (a, b) -> {
            if (a[0] != b[0]) {
                return Integer.compare(b[0], a[0]);
            }
            return Integer.compare(b[1], a[1]);
        });

        List<Integer> answer = new ArrayList<>();
        for (int[] restaurant : filtered) {
            answer.add(restaurant[1]);
        }
        return answer;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * Filter first, then sort. Keep restaurants that satisfy the vegan, price, and
 * distance rules. Sort survivors by rating descending and id descending.
 *
 * Java data structures:
 * A `List<int[]>` stores `[rating, id]` pairs. A custom comparator implements
 * the required ordering, and a final `List<Integer>` returns ids only.
 *
 * Edge cases:
 * - veganFriendly = 0 means vegan status is ignored.
 * - Tied ratings are ordered by larger id first.
 * - If no restaurants pass filters, return an empty list.
 *
 * Complexity:
 * Time O(n log n), dominated by sorting filtered restaurants.
 * Space O(n) in the worst case.
 */
