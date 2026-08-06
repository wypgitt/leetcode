package leetcode

//
// @lc app=leetcode id=3899 lang=golang
//
// [3899] Angles of a Triangle
//
// Notes
// Sort side lengths to validate the triangle inequality. For each side, apply
// the law of cosines to compute the opposite angle, clamp cosine into [-1,1] to
// avoid floating-point drift, then return the three angles sorted. Time:
// O(1). Space: O(1).
//
// @lc code=start

import (
	"math"
	"sort"
)

func InternalAngles3899(sides []int) []float64 {
	values := append([]int(nil), sides...)
	sort.Ints(values)
	a, b, c := values[0], values[1], values[2]
	if a+b <= c {
		return []float64{}
	}

	angles := []float64{
		angle3899(a, b, c),
		angle3899(b, a, c),
		angle3899(c, a, b),
	}
	sort.Float64s(angles)
	return angles
}

func angle3899(opposite int, side1 int, side2 int) float64 {
	cosValue := float64(side1*side1+side2*side2-opposite*opposite) / float64(2*side1*side2)
	if cosValue < -1.0 {
		cosValue = -1.0
	}
	if cosValue > 1.0 {
		cosValue = 1.0
	}
	return math.Acos(cosValue) * 180.0 / math.Pi
}

// @lc code=end
