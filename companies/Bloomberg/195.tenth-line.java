/*
 * =============================================================================
 * WHY YOU SEE: Not supported language "python3" / Command failed for LeetCode 195
 * =============================================================================
 *
 * Problem 195 is tagged **shell** only. The LeetCode CLI only accepts **bash** for
 * this problem.
 *
 * **Fix — switch the active language to Bash for this problem** and use
 *   195.tenth-line.sh
 * for submission.
 *
 * =============================================================================
 * INTERVIEW / NOTES (problem 195 — Tenth Line)
 * =============================================================================
 *
 * Task: Read file.txt, print **only** the 10th line.
 *
 * If fewer than 10 lines: Print **nothing** (empty stdout). Matches sed -n '10p'.
 *
 * Three classic approaches:
 *
 *   1. sed -n '10p' file.txt
 *   2. awk 'NR==10' file.txt
 *   3. head -n 10 | tail -n 1 — wrong if fewer than 10 lines (tail prints last line).
 *
 * Complexity: O(n) to reach line 10 worst case; O(1) extra space for streaming.
 *
 * This Java file is a **reference** for local testing only — not the LC submission.
 * =============================================================================
 */

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

/** Local reference: print 10th line of file (1-based), or nothing if missing. */
public class TenthLine {
    public static void printTenthLine(Path path) throws IOException {
        List<String> lines = Files.readAllLines(path, StandardCharsets.UTF_8);
        if (lines.size() >= 10) {
            System.out.print(lines.get(9));
        }
    }

    public static void main(String[] args) throws IOException {
        printTenthLine(Path.of(args.length > 0 ? args[0] : "file.txt"));
    }
}
