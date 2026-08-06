package leetcode

import "strings"

// SplitLoopedString555 chooses the lexicographically larger orientation for
// every non-boundary string. Then it tries each string as the boundary string,
// both orientations, and every split point.
//
// Time: O(L^2) with naive candidate construction, accepted by the constraints.
// Space: O(L) for candidates and fixed orientations.
func SplitLoopedString555(strs []string) string {
	parts := make([]string, len(strs))
	for i, s := range strs {
		r := reverseString(s)
		if r > s {
			parts[i] = r
		} else {
			parts[i] = s
		}
	}
	best := ""
	for i, original := range strs {
		middle := strings.Join(append(append([]string{}, parts[i+1:]...), parts[:i]...), "")
		for _, src := range []string{original, reverseString(original)} {
			for cut := 0; cut < len(src); cut++ {
				candidate := src[cut:] + middle + src[:cut]
				if candidate > best {
					best = candidate
				}
			}
		}
	}
	return best
}
