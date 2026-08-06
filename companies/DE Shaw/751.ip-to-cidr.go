package leetcode

import (
	"fmt"
	"math/bits"
	"strconv"
	"strings"
)

// IpToCIDR751 converts the start IP to a 32-bit integer, then repeatedly emits
// the largest aligned power-of-two block that does not exceed the remaining
// count. Alignment is limited by the current address lowbit.
//
// Time: O(number of emitted CIDR blocks * 32). Space: O(output).
func IpToCIDR751(ip string, n int) []string {
	ipToInt := func(s string) uint32 {
		var value uint32
		for _, part := range strings.Split(s, ".") {
			x, _ := strconv.Atoi(part)
			value = value*256 + uint32(x)
		}
		return value
	}
	intToIP := func(x uint32) string {
		return fmt.Sprintf("%d.%d.%d.%d", byte(x>>24), byte(x>>16), byte(x>>8), byte(x))
	}
	start := ipToInt(ip)
	ans := []string{}
	for n > 0 {
		block := int(start & -start)
		if block == 0 {
			block = 1 << 32
		}
		for block > n {
			block >>= 1
		}
		prefix := 32 - (bits.Len(uint(block)) - 1)
		ans = append(ans, fmt.Sprintf("%s/%d", intToIP(start), prefix))
		start += uint32(block)
		n -= block
	}
	return ans
}
