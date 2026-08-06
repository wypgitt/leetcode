package leetcode

//
// @lc app=leetcode id=469 lang=golang
//
// [469] Convex Polygon
//
// Notes
// Traverse triples of consecutive vertices and inspect cross-product signs. A
// convex polygon never changes turn direction; collinear triples are ignored.
// Any nonzero turn opposite to the first nonzero turn proves non-convexity.
// Time: O(n). Space: O(1).
//
// @lc code=start

func IsConvex469(points [][]int) bool {
	turnSign := 0
	pointCount := len(points)
	for index := 0; index < pointCount; index++ {
		currentCross := cross469(points[index], points[(index+1)%pointCount], points[(index+2)%pointCount])
		if currentCross == 0 {
			continue
		}
		currentSign := 1
		if currentCross < 0 {
			currentSign = -1
		}
		if turnSign == 0 {
			turnSign = currentSign
		} else if currentSign != turnSign {
			return false
		}
	}
	return true
}

func cross469(a, b, c []int) int {
	return (b[0]-a[0])*(c[1]-b[1]) - (b[1]-a[1])*(c[0]-b[0])
}

// @lc code=end
