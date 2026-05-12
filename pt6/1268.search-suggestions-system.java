import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

class Solution {
    public List<List<String>> suggestedProducts(String[] products, String searchWord) {
        Arrays.sort(products);
        List<List<String>> ans = new ArrayList<>();
        StringBuilder prefix = new StringBuilder();

        for (char ch : searchWord.toCharArray()) {
            prefix.append(ch);
            String current = prefix.toString();
            int start = lowerBound(products, current);
            List<String> suggestions = new ArrayList<>();

            for (int i = start; i < products.length && i < start + 3; i++) {
                if (products[i].startsWith(current)) {
                    suggestions.add(products[i]);
                }
            }
            ans.add(suggestions);
        }

        return ans;
    }

    private int lowerBound(String[] products, String target) {
        int left = 0;
        int right = products.length;
        while (left < right) {
            int mid = left + (right - left) / 2;
            if (products[mid].compareTo(target) < 0) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }
        return left;
    }
}

/*
Explanation

Sort products lexicographically. For each prefix of searchWord, binary search
for the first product not less than the prefix, then inspect at most the next
three products.

Sorting works because all strings with the same prefix form one contiguous
range. This is a compact alternative to a trie when only three suggestions are
needed.

Edge cases: fewer than three matches; no matches; one product being a prefix of
another.

Time complexity: O(n log n + m log n + 3mL), where m is searchWord length.
Space complexity: O(m) for the answer lists, excluding sorting.
*/
