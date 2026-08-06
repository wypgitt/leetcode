/*
 * LeetCode 194 — Transpose File
 *
 * =============================================================================
 * IMPORTANT: Official judge language is SHELL (Bash), not Java
 * =============================================================================
 *
 * On LeetCode, open the Shell environment and paste the script from:
 *   194.transpose-file.sh
 * (same awk logic as documented below).
 *
 * This .java file mirrors the Python reference: interview notes + local runnable
 * transpose utility (see {@link TransposeFile#main}).
 *
 * =============================================================================
 * INTERVIEW: HOW TO EXPLAIN (elevator → whiteboard)
 * =============================================================================
 *
 * 30 seconds:
 *   "Read the file as a matrix of words split on spaces. The transpose swaps
 *   rows and columns: output line k is the concatenation of column k from every
 *   original row, space-separated."
 *
 * =============================================================================
 * ALGORITHM
 * =============================================================================
 *
 * Let rows be tokenized lines with C columns (constant per problem assumption).
 * Output row j is: field_j from line_1, space, field_j from line_2, ...
 * Equivalently: matrix transpose T where T[j][i] = original[i][j].
 *
 * =============================================================================
 * COMPLEXITY
 * =============================================================================
 *
 * Time:  O(R * C). Space: O(R * C) for materialized grid (same order as output size).
 *
 * =============================================================================
 * EDGE CASES
 * =============================================================================
 *
 * - Empty file: nothing to print.
 * - Single row: transpose is one word per line per column.
 * - Ragged rows: problem assumes rectangular input; robust code may pad or error.
 *
 * =============================================================================
 */

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/** Local reference — not the LeetCode submission format for problem 194. */
public class TransposeFile {

    public static void transposeAndPrint(Path path) throws IOException {
        List<String> rawLines = Files.readAllLines(path, StandardCharsets.UTF_8);
        List<List<String>> lines = new ArrayList<>();
        for (String raw : rawLines) {
            String t = raw.trim();
            if (t.isEmpty()) {
                continue;
            }
            lines.add(Arrays.asList(t.split("\\s+")));
        }
        if (lines.isEmpty()) {
            return;
        }
        int cols = lines.get(0).size();
        for (List<String> row : lines) {
            if (row.size() != cols) {
                throw new IllegalArgumentException("ragged rows: column counts differ");
            }
        }
        for (int c = 0; c < cols; c++) {
            StringBuilder sb = new StringBuilder();
            for (int r = 0; r < lines.size(); r++) {
                if (r > 0) {
                    sb.append(' ');
                }
                sb.append(lines.get(r).get(c));
            }
            System.out.println(sb);
        }
    }

    public static void main(String[] args) throws IOException {
        Path p = Path.of(args.length > 0 ? args[0] : "file.txt");
        if (!Files.isRegularFile(p)) {
            System.err.println("Expected " + p + " to exist.");
            System.exit(1);
        }
        transposeAndPrint(p);
    }
}
