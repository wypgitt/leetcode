package leetcode

// LogSystem635 stores timestamp/id pairs and compares timestamp prefixes. The
// timestamp format is zero-padded from most to least significant field, so
// lexicographic prefix order matches chronological order at that granularity.
type LogSystem635 struct {
	logs  []logEntry635
	index map[string]int
}

type logEntry635 struct {
	timestamp string
	id        int
}

func Constructor635() LogSystem635 {
	return LogSystem635{index: map[string]int{"Year": 4, "Month": 7, "Day": 10, "Hour": 13, "Minute": 16, "Second": 19}}
}

func (ls *LogSystem635) Put(id int, timestamp string) {
	ls.logs = append(ls.logs, logEntry635{timestamp: timestamp, id: id})
}

// Retrieve is O(L) over stored logs and returns IDs with inclusive boundaries.
func (ls *LogSystem635) Retrieve(start string, end string, granularity string) []int {
	cut := ls.index[granularity]
	lo, hi := start[:cut], end[:cut]
	ans := []int{}
	for _, entry := range ls.logs {
		prefix := entry.timestamp[:cut]
		if lo <= prefix && prefix <= hi {
			ans = append(ans, entry.id)
		}
	}
	return ans
}
