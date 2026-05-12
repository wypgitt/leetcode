import java.util.HashMap;
import java.util.Map;

/*
 * LeetCode 1357 - Apply Discount Every n Orders
 */
class Cashier {
    private final int n;
    private final int discount;
    private final Map<Integer, Integer> priceByProduct;
    private int customerCount;

    public Cashier(int n, int discount, int[] products, int[] prices) {
        this.n = n;
        this.discount = discount;
        this.customerCount = 0;
        this.priceByProduct = new HashMap<>();

        for (int i = 0; i < products.length; i++) {
            priceByProduct.put(products[i], prices[i]);
        }
    }

    public double getBill(int[] product, int[] amount) {
        customerCount++;
        double total = 0.0;

        for (int i = 0; i < product.length; i++) {
            total += priceByProduct.get(product[i]) * amount[i];
        }

        if (customerCount % n == 0) {
            total *= (100 - discount) / 100.0;
        }

        return total;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * Store prices for O(1) lookup and count how many customers have been served.
 * Every nth customer gets the percentage discount.
 *
 * Java data structures:
 * `HashMap<Integer, Integer>` maps product id to price. Primitive fields store
 * the discount rule and customer count.
 *
 * Edge cases:
 * - Multiple items in an order are summed as price * amount.
 * - Non-discount customers return the raw total.
 * - Discount customers multiply by `(100 - discount) / 100.0`.
 *
 * Complexity:
 * Constructor O(p), where p is number of products.
 * getBill O(k), where k is number of product entries in the order.
 * Space O(p).
 */
