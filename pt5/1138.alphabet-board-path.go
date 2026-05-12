package main

import "strings"

func alphabetBoardPath(target string) string {
	row, col := 0, 0
	var builder strings.Builder

	for _, char := range target {
		index := int(char - 'a')
		nextRow, nextCol := index/5, index%5

		for row > nextRow {
			builder.WriteByte('U')
			row--
		}
		for col > nextCol {
			builder.WriteByte('L')
			col--
		}
		for col < nextCol {
			builder.WriteByte('R')
			col++
		}
		for row < nextRow {
			builder.WriteByte('D')
			row++
		}
		builder.WriteByte('!')
	}

	return builder.String()
}

