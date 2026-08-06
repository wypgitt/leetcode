/*
 * @lc app=leetcode id=604 lang=java
 *
 * [604] Design Compressed String Iterator
 *
 * Lazily parse one compressed group at a time. currentChar and remaining hold
 * the active run; when remaining reaches zero, parse the next letter and its
 * decimal count. This avoids expanding huge counts.
 *
 * Time: O(1) amortized per call. Space: O(1).
 */

// @lc code=start
class StringIterator {
    private final String compressed;
    private int index;
    private char currentChar;
    private int remaining;

    public StringIterator(String compressedString) {
        this.compressed = compressedString;
    }

    public char next() {
        if (!hasNext()) {
            return ' ';
        }
        remaining--;
        return currentChar;
    }

    public boolean hasNext() {
        if (remaining > 0) {
            return true;
        }
        loadNextGroup();
        return remaining > 0;
    }

    private void loadNextGroup() {
        if (index >= compressed.length()) {
            return;
        }
        currentChar = compressed.charAt(index++);
        int count = 0;
        while (index < compressed.length() && Character.isDigit(compressed.charAt(index))) {
            count = count * 10 + compressed.charAt(index) - '0';
            index++;
        }
        remaining = count;
    }
}
// @lc code=end
