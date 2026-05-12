package main

import (
	"fmt"
	"sort"
	"strconv"
	"strings"
)

/*
1058. Minimize Rounding Error to Meet Target
*/
func minimizeError(prices []string, target int) string {
	floorSum := 0
	fractions := make([]int, 0, len(prices))

	for _, price := range prices {
		parts := strings.Split(price, ".")
		whole, _ := strconv.Atoi(parts[0])
		fraction, _ := strconv.Atoi(parts[1])

		floorSum += whole
		if fraction != 0 {
			fractions = append(fractions, fraction)
		}
	}

	ceilingsNeeded := target - floorSum
	if ceilingsNeeded < 0 || ceilingsNeeded > len(fractions) {
		return "-1"
	}

	sort.Sort(sort.Reverse(sort.IntSlice(fractions)))
	errorThousandths := 0
	for _, fraction := range fractions {
		errorThousandths += fraction
	}

	for i := 0; i < ceilingsNeeded; i++ {
		errorThousandths += 1000 - 2*fractions[i]
	}

	return fmt.Sprintf("%d.%03d", errorThousandths/1000, errorThousandths%1000)
}

/*
Interview Explanation

Core idea:
Start by flooring every price. If the floor sum is short of target by k, then
exactly k non-integer prices must be rounded up. To minimize error, round up
the largest fractional parts.

Go data structures:
- []int fractions stores fractional thousandths, avoiding floating-point error.
- sort.Reverse(sort.IntSlice(...)) sorts fractions descending.

Algorithm:
1. Parse each price into whole and fractional thousandths.
2. Sum all floor values.
3. Store nonzero fractions.
4. ceilingsNeeded = target - floorSum.
5. If that count is impossible, return "-1".
6. Base error from flooring is sum(fractions).
7. Rounding fraction f up changes error from f to 1000-f, a delta of
   1000-2*f. Apply that delta to the largest fractions.
8. Format as exactly three decimal places.

Correctness:
The target fixes exactly how many prices must be ceiled. For two fractions
a > b, ceiling a instead of b has smaller error delta because 1000-2a is less
than 1000-2b. Therefore an optimal solution ceilings the k largest fractions,
which the algorithm does.

Complexity:
Parsing is O(n), sorting is O(n log n), and space is O(n).

Edge cases:
- Target below all floors or above all ceilings returns -1.
- Integer prices have no rounding choice and no error.
- Formatting always includes three digits after the decimal point.
*/
