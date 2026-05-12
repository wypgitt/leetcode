import java.util.ArrayList;
import java.util.List;

class CombinationIterator {
    private final List<String> combinations = new ArrayList<>();
    private int index = 0;

    public CombinationIterator(String characters, int combinationLength) {
        build(characters, combinationLength, 0, new StringBuilder());
    }

    public String next() {
        return combinations.get(index++);
    }

    public boolean hasNext() {
        return index < combinations.size();
    }

    private void build(String characters, int targetLength, int start, StringBuilder path) {
        if (path.length() == targetLength) {
            combinations.add(path.toString());
            return;
        }

        int need = targetLength - path.length();
        for (int i = start; i <= characters.length() - need; i++) {
            path.append(characters.charAt(i));
            build(characters, targetLength, i + 1, path);
            path.deleteCharAt(path.length() - 1);
        }
    }
}

/*
Explanation

Precompute all combinations using backtracking. Since characters are sorted and
we choose increasing indices, the combinations are generated in lexicographic
order. The iterator then only stores an index into the list.

This is a good Java design tradeoff for the constraints: next and hasNext are
O(1), and the number of combinations is small enough to store.

Edge cases: only one combination; repeated hasNext calls do not advance; next
advances exactly once.

Constructor time and space: O(C * L), where C is the number of combinations and
L is combinationLength. next and hasNext: O(1).
*/
