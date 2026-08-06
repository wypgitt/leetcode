package leetcode

import (
	"math"
	"math/rand"
)

// RandomPoint478 stores a circle and samples points uniformly by choosing an
// angle uniformly and radius as R*sqrt(U). The square root is required because
// circle area grows with r^2; a uniform radius would over-sample the center.
type RandomPoint478 struct {
	radius  float64
	xCenter float64
	yCenter float64
}

func Constructor478(radius float64, xCenter float64, yCenter float64) RandomPoint478 {
	return RandomPoint478{radius: radius, xCenter: xCenter, yCenter: yCenter}
}

// RandPoint returns one uniformly random point in the circle.
// Time: O(1). Space: O(1).
func (rp *RandomPoint478) RandPoint() []float64 {
	angle := rand.Float64() * 2 * math.Pi
	distance := rp.radius * math.Sqrt(rand.Float64())
	return []float64{rp.xCenter + distance*math.Cos(angle), rp.yCenter + distance*math.Sin(angle)}
}
