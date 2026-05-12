import java.util.ArrayList;
import java.util.List;

/*
 * LeetCode 1352 - Product of the Last K Numbers
 */
class ProductOfNumbers {
    private List<Integer> prefixProducts;

    public ProductOfNumbers() {
        prefixProducts = new ArrayList<>();
        prefixProducts.add(1);
    }

    public void add(int num) {
        if (num == 0) {
            prefixProducts = new ArrayList<>();
            prefixProducts.add(1);
        } else {
            prefixProducts.add(prefixProducts.get(prefixProducts.size() - 1) * num);
        }
    }

    public int getProduct(int k) {
        if (k >= prefixProducts.size()) {
            return 0;
        }

        int last = prefixProducts.get(prefixProducts.size() - 1);
        int beforeWindow = prefixProducts.get(prefixProducts.size() - 1 - k);
        return last / beforeWindow;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * Products over a suffix can be answered with prefix products:
 * product(last k) = prefix[last] / prefix[before window]. Zeros reset the
 * prefix list because any query reaching before the reset contains a zero.
 *
 * Java data structures:
 * `ArrayList<Integer>` stores prefix products since the most recent zero. The
 * sentinel 1 at index 0 makes division work when k equals the current nonzero
 * segment length.
 *
 * Edge cases:
 * - Adding zero resets the product history.
 * - If k reaches before the current nonzero segment, return 0.
 * - LeetCode guarantees products fit in 32-bit int.
 *
 * Complexity:
 * add O(1), getProduct O(1).
 * Space O(m), where m is count of consecutive nonzero values after last zero.
 */
