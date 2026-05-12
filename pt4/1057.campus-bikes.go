package main

/*
1057. Campus Bikes
*/
func assignBikes(workers [][]int, bikes [][]int) []int {
	buckets := make([][][2]int, 2000)

	for workerIndex, worker := range workers {
		for bikeIndex, bike := range bikes {
			distance := abs1057(worker[0]-bike[0]) + abs1057(worker[1]-bike[1])
			buckets[distance] = append(buckets[distance], [2]int{workerIndex, bikeIndex})
		}
	}

	assignment := make([]int, len(workers))
	for i := range assignment {
		assignment[i] = -1
	}
	bikeUsed := make([]bool, len(bikes))
	assigned := 0

	for _, bucket := range buckets {
		for _, pair := range bucket {
			workerIndex, bikeIndex := pair[0], pair[1]
			if assignment[workerIndex] == -1 && !bikeUsed[bikeIndex] {
				assignment[workerIndex] = bikeIndex
				bikeUsed[bikeIndex] = true
				assigned++
				if assigned == len(workers) {
					return assignment
				}
			}
		}
	}

	return assignment
}

func abs1057(value int) int {
	if value < 0 {
		return -value
	}
	return value
}

/*
Interview Explanation

Core idea:
The assignment rule is global ordering by (distance, worker index, bike index).
Coordinates are less than 1000, so Manhattan distance is at most 1998. Bucket
sort processes pairs in the exact required order.

Go data structures:
- [][][2]int buckets groups worker-bike pairs by distance.
- []int assignment records the bike for each worker.
- []bool bikeUsed marks bikes that are no longer available.

Algorithm:
1. Generate every worker-bike pair.
2. Append it to the bucket for its Manhattan distance. The nested loops already
   create pairs in worker-index then bike-index order inside each bucket.
3. Scan buckets from smallest distance to largest.
4. Assign a pair if both worker and bike are still free.
5. Stop once all workers are assigned.

Correctness:
Bucket order gives increasing distance, and insertion order inside a bucket
matches the tie-breakers. Skipping unavailable workers and bikes mirrors the
problem's repeated selection process. Thus every assigned pair is exactly the
pair the rules would choose.

Complexity:
Let W be workers and B be bikes. Generating and scanning pairs costs O(W*B).
Space is O(W*B) for buckets.

Edge cases:
- Distance ties are resolved by worker then bike index.
- Extra bikes remain unused.
- One worker receives the nearest bike.
*/
