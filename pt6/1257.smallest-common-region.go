package main

func findSmallestRegion(regions [][]string, region1 string, region2 string) string {
	parent := map[string]string{}
	for _, group := range regions {
		root := group[0]
		for i := 1; i < len(group); i++ {
			parent[group[i]] = root
		}
	}

	ancestors := map[string]bool{}
	for cur := region1; cur != ""; cur = parent[cur] {
		ancestors[cur] = true
		if _, ok := parent[cur]; !ok {
			break
		}
	}

	for cur := region2; ; cur = parent[cur] {
		if ancestors[cur] {
			return cur
		}
	}
}

/*
Explanation

The region hierarchy is a tree. Build child -> parent pointers from the input.
Then add all ancestors of region1 to a set and climb from region2 until the
first common ancestor is found. That first common ancestor is the smallest
common region.

The parent map is sufficient because every region has at most one direct
parent.

Edge cases: one region is an ancestor of the other; both regions are equal; the
answer can be the global root.

Time complexity: O(N), where N is the number of region names.
Space complexity: O(N).
*/
