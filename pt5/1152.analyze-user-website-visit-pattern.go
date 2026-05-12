package main

import "sort"

type visitRecord struct {
	user string
	time int
	site string
}

func mostVisitedPattern(username []string, timestamp []int, website []string) []string {
	visits := make([]visitRecord, len(username))
	for i := range username {
		visits[i] = visitRecord{user: username[i], time: timestamp[i], site: website[i]}
	}
	sort.Slice(visits, func(i, j int) bool {
		return visits[i].time < visits[j].time
	})

	byUser := map[string][]string{}
	for _, visit := range visits {
		byUser[visit.user] = append(byUser[visit.user], visit.site)
	}

	counts := map[[3]string]int{}
	for _, sites := range byUser {
		seen := map[[3]string]bool{}
		for i := 0; i < len(sites); i++ {
			for j := i + 1; j < len(sites); j++ {
				for k := j + 1; k < len(sites); k++ {
					pattern := [3]string{sites[i], sites[j], sites[k]}
					seen[pattern] = true
				}
			}
		}
		for pattern := range seen {
			counts[pattern]++
		}
	}

	if len(counts) == 0 {
		return []string{}
	}

	var best [3]string
	bestCount := -1
	first := true
	for pattern, count := range counts {
		if first || count > bestCount || count == bestCount && lessPattern(pattern, best) {
			first = false
			best = pattern
			bestCount = count
		}
	}

	return []string{best[0], best[1], best[2]}
}

func lessPattern(a, b [3]string) bool {
	for i := 0; i < 3; i++ {
		if a[i] != b[i] {
			return a[i] < b[i]
		}
	}
	return false
}

