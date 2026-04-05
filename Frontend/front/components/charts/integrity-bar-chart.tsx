"use client"

import { useEffect, useRef } from "react"
import * as d3 from "d3"

type Datum = { source: string; citations: number }

const defaultData: Datum[] = [
  { source: "Journal A", citations: 12 },
  { source: "Conf B", citations: 7 },
  { source: "Archive C", citations: 18 },
  { source: "Book D", citations: 5 },
  { source: "Dataset E", citations: 9 },
]

export function IntegrityBarChart({ data = defaultData }: { data?: Datum[] }) {
  const ref = useRef<SVGSVGElement | null>(null)

  useEffect(() => {
    const svg = d3.select(ref.current)
    svg.selectAll("*").remove()

    const width = 560
    const height = 280
    const margin = { top: 20, right: 20, bottom: 36, left: 80 }

    svg.attr("viewBox", `0 0 ${width} ${height}`)

    const x = d3
      .scaleLinear()
      .domain([0, d3.max(data, (d) => d.citations)!])
      .nice()
      .range([margin.left, width - margin.right])

    const y = d3
      .scaleBand()
      .domain(data.map((d) => d.source))
      .range([margin.top, height - margin.bottom])
      .padding(0.2)

    const bars = svg
      .append("g")
      .selectAll("rect")
      .data(data)
      .join("rect")
      .attr("x", x(0))
      .attr("y", (d) => y(d.source)!)
      .attr("height", y.bandwidth())
      .attr("width", (d) => x(d.citations) - x(0))
      .attr("rx", 6)
      .attr("fill", "blue")
      .attr("opacity", 0.9)

    // Use CSS currentColor to inherit from surrounding text color.
    // Add axes
    const xAxis = (g: d3.Selection<SVGGElement, unknown, null, undefined>) =>
      g
        .attr("transform", `translate(0,${height - margin.bottom})`)
        .call(d3.axisBottom(x).ticks(6))
        .call((s) => s.selectAll("text").attr("font-size", 10))

    const yAxis = (g: d3.Selection<SVGGElement, unknown, null, undefined>) =>
      g
        .attr("transform", `translate(${margin.left},0)`)
        .call(d3.axisLeft(y).tickSizeOuter(0))
        .call((s) => s.selectAll("text").attr("font-size", 11))

    svg.append("g").call(xAxis)
    svg.append("g").call(yAxis)

    // Accessibility: add titles
    bars.append("title").text((d) => `${d.source}: ${d.citations}`)
  }, [data])

  return (
    <div className="text-primary">
      <svg ref={ref} role="img" aria-label="Citation counts by source" />
    </div>
  )
}
