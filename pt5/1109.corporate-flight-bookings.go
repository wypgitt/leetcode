package main

func corpFlightBookings(bookings [][]int, n int) []int {
	diff := make([]int, n+1)
	for _, booking := range bookings {
		first, last, seats := booking[0], booking[1], booking[2]
		diff[first-1] += seats
		diff[last] -= seats
	}

	answer := make([]int, n)
	running := 0
	for i := 0; i < n; i++ {
		running += diff[i]
		answer[i] = running
	}
	return answer
}

