/**
 * Algorithm:
 * Keep row and column pointers. Before next or hasNext, skip empty rows until
 * row points to an available value or reaches the end.
 *
 * Java data structures:
 * int[][] stores the input vector; row/col are cursor indices.
 *
 * Complexity:
 * next and hasNext are O(1) amortized; space O(1).
 */
class Vector2D {
    private final int[][] vec;
    private int row;
    private int col;

    public Vector2D(int[][] vec) {
        this.vec = vec;
        row = 0;
        col = 0;
    }

    public int next() {
        skipEmpty();
        return vec[row][col++];
    }

    public boolean hasNext() {
        skipEmpty();
        return row < vec.length;
    }

    private void skipEmpty() {
        while (row < vec.length && col >= vec[row].length) {
            row++;
            col = 0;
        }
    }
}

