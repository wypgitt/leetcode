package leetcode

//
// @lc app=leetcode id=3860 lang=golang
//
// [3860] Unique Email Groups
//
// Notes
// Normalize each email by lowercasing the local/domain parts, dropping anything
// after '+', and removing dots from the local part. A Go map[string]struct{} is
// used as the set of normalized addresses. Time: O(total characters). Space:
// O(number of emails).
//
// @lc code=start

import "strings"

func UniqueEmailGroups3860(emails []string) int {
	normalized := map[string]struct{}{}
	for _, email := range emails {
		parts := strings.SplitN(email, "@", 2)
		local := strings.ToLower(parts[0])
		if plus := strings.IndexByte(local, '+'); plus != -1 {
			local = local[:plus]
		}
		local = strings.ReplaceAll(local, ".", "")
		domain := strings.ToLower(parts[1])
		normalized[local+"@"+domain] = struct{}{}
	}
	return len(normalized)
}

// @lc code=end
