package leetcode

import "strings"

// SimplifyPath71 is stack-based Unix path normalization. Directory names push,
// ".." pops when possible, and "." or empty components from repeated slashes do
// nothing. Joining the stack yields the canonical absolute path.
//
// Time: O(n). Space: O(n).
func SimplifyPath71(path string) string {
	stack := []string{}
	for _, part := range strings.Split(path, "/") {
		if part == "" || part == "." {
			continue
		}
		if part == ".." {
			if len(stack) > 0 {
				stack = stack[:len(stack)-1]
			}
		} else {
			stack = append(stack, part)
		}
	}
	return "/" + strings.Join(stack, "/")
}
