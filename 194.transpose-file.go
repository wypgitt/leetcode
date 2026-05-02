package leetcode

//
// LeetCode 194 — Transpose File
//
// =============================================================================
// IMPORTANT: Official judge language is SHELL (Bash), not Python
// =============================================================================
//
// On LeetCode, open the Shell environment and paste the script from:
//   194.transpose-file.sh
// (same awk logic as the Python reference below).
//
// This .go file is for: interview notes + a reference implementation you can run
// locally alongside other tooling.
//
// =============================================================================
// INTERVIEW: HOW TO EXPLAIN (elevator → whiteboard)
// =============================================================================
//
// 30 seconds:
//   "Read the file as a matrix of words split on spaces. The transpose swaps
//   rows and columns: output line k is the concatenation of column k from every
//   original row, space-separated. One pass can accumulate each column into a
//   string; in shell, awk is ideal because it already tokenizes fields."
//
// 2–4 minutes:
//   - Clarify I/O: input file.txt, fields separated by single spaces (problem
//     often assumes rectangular input — same number of columns per row).
//   - Naive: load whole file into memory as [][]string, then for each
//     column index j, join rows[i][j] for i in 0..R-1 — O(R*C) time, O(R*C)
//     space if we materialize the grid.
//   - Streaming column-wise accumulate (awk): for each line, for each field
//     index i, append $i to array line[i] with a leading space after row 1.
//     After all lines, print line[1]..line[NF] in order (NF from last row =
//     column count when rectangular).
//   - Why awk on LC: field splitting is built-in; no manual split loops.
//
// =============================================================================
// ALGORITHM
// =============================================================================
//
// Let rows be tokenized lines with C columns (constant per problem assumption).
// Output row j (1-based field index) is: field_j from line_1, space, field_j
// from line_2, space, … for all lines.
//
// Equivalently: matrix transpose T where T[j][i] = original[i][j].
//
// awk implementation:
//   For each input record (line), for i from 1 to NF:
//       line[i] := line[i] + (space if not first row) + $i
//   END: for i from 1 to NF: print line[i]
//
// Ordering: forward iteration 1..NF preserves column order in output.
//
// =============================================================================
// DATA STRUCTURES
// =============================================================================
//
// - awk associative array `line` indexed by column number (1..NF), values are
//   strings being built for each transposed row.
// - Python reference: list of lists `grid`, or column-wise join without full
//   grid if streaming line-by-line into []string per column index.
//
// Space:
//   - awk: O(C * R) characters stored across C strings (same as output size).
//   - Problem fits in memory on LC; streaming print could be discussed but rare.
//
// =============================================================================
// COMPLEXITY
// =============================================================================
//
// Let R = number of lines, C = columns (max NF).
// Time:  O(R * C) — touch each field once.
// Space: O(R * C) output-sized storage for accumulated strings (same order as
//        reading full matrix in Python).
//
// =============================================================================
// EDGE CASES
// =============================================================================
//
// - Empty file: nothing to print (awk END loop with NF=0 prints nothing).
// - Single row: transpose is one word per line (each original column becomes its
//   own output line) — matches matrix transpose definition.
// - Single column: one output line with R words separated by spaces.
// - Ragged rows (not assumed by LC statement): real systems must define behavior;
//   robust Python pads missing cells or errors; awk uses per-line NF (advanced).
// - Trailing spaces on lines: strip if needed; LC inputs are usually clean.
//
// =============================================================================
// TESTING
// =============================================================================
//
// Golden file test:
//   Create file.txt with the sample (name/age example), run script, diff expected.
// Unit-style checks:
//   - 2x2 identity words → transpose swaps off-diagonal conceptually.
//   - Random small matrices: transpose(transpose(A)) == A for rectangular grid.
// Shell:
//   bash 194.transpose-file.sh | diff - expected.txt
//
// =============================================================================

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

// TransposeFile194 reads space-separated tokens from path and returns transposed lines.
// Each element is one output line (column-wise join). Mirrors the awk algorithm:
// column j is the j-th token of each input row joined with spaces.
//
// Returns an error if the file does not exist or rows have differing column counts.
func TransposeFile194(path string) ([]string, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, fmt.Errorf("expected %s to exist: %w", path, err)
	}
	defer f.Close()

	var lines [][]string
	sc := bufio.NewScanner(f)
	for sc.Scan() {
		raw := strings.TrimSpace(sc.Text())
		if raw == "" {
			continue
		}
		row := strings.Fields(raw)
		lines = append(lines, row)
	}
	if err := sc.Err(); err != nil {
		return nil, err
	}

	if len(lines) == 0 {
		return nil, nil
	}

	cols := len(lines[0])
	for _, row := range lines {
		if len(row) != cols {
			return nil, fmt.Errorf("ragged rows: column counts differ (problem assumes fixed width)")
		}
	}

	out := make([]string, cols)
	for c := 0; c < cols; c++ {
		parts := make([]string, len(lines))
		for r := range lines {
			parts[r] = lines[r][c]
		}
		out[c] = strings.Join(parts, " ")
	}
	return out, nil
}

// TransposeAndPrint194 reads path and prints transposed lines to stdout (reference behavior).
func TransposeAndPrint194(path string) error {
	lines, err := TransposeFile194(path)
	if err != nil {
		fmt.Fprintf(os.Stderr, "%v\n", err)
		return err
	}
	for _, ln := range lines {
		fmt.Println(ln)
	}
	return nil
}
