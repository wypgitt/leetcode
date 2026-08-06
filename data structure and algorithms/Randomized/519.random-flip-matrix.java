import java.util.*;

/**
 * Algorithm:
 * Simulate drawing a random unused index from [0, remaining). A hash map stores
 * swaps from picked positions to the actual remaining tail positions, giving
 * Fisher-Yates behavior without materializing the whole matrix.
 *
 * Java data structures:
 * HashMap<Integer, Integer> stores sparse remaps. Random.nextInt(bound) chooses
 * a uniform remaining index.
 *
 * Complexity:
 * flip and reset are O(1) average time. Space is O(number of flips since reset).
 */
class Solution {
    private final int m;
    private final int n;
    private final int total;
    private int remaining;
    private final Map<Integer, Integer> remap;
    private final Random random;

    public Solution(int m, int n) {
        this.m = m;
        this.n = n;
        this.total = m * n;
        this.remaining = total;
        this.remap = new HashMap<>();
        this.random = new Random();
    }

    public int[] flip() {
        int pick = random.nextInt(remaining);
        remaining--;
        int actual = remap.getOrDefault(pick, pick);
        remap.put(pick, remap.getOrDefault(remaining, remaining));
        return new int[] {actual / n, actual % n};
    }

    public void reset() {
        remaining = total;
        remap.clear();
    }
}

