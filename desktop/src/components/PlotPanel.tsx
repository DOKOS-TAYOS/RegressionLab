import Plot from "react-plotly.js";

import type { PlotPayload } from "@/types";

type PlotPanelProps = {
  plot: PlotPayload;
};

export function PlotPanel({ plot }: PlotPanelProps) {
  const rootStyle = getComputedStyle(document.documentElement);
  const accentMain = rootStyle.getPropertyValue("--accent-main").trim() || "#7de76a";
  const accentAlt = rootStyle.getPropertyValue("--accent-alt").trim() || "#e6d954";
  const textColor = rootStyle.getPropertyValue("--fg-base").trim() || "#d8d8d8";
  const gridColor = "rgba(255,255,255,0.08)";
  const axisTitle = (text: string) => ({
    text,
    font: { color: textColor },
  });

  if (plot.kind === "curve2d") {
    return (
      <Plot
        className="plot"
        data={plot.traces.map((trace) =>
          trace.mode === "markers"
            ? {
                type: "scatter",
                mode: "markers",
                name: trace.name,
                x: trace.x,
                y: trace.y,
                error_x: trace.errorX ? { type: "data", array: trace.errorX, visible: true } : undefined,
                error_y: trace.errorY ? { type: "data", array: trace.errorY, visible: true } : undefined,
                marker: { size: 8, color: accentMain, line: { width: 1, color: "#f7f7f7" } },
              }
            : {
                type: "scatter",
                mode: "lines",
                name: trace.name,
                x: trace.x,
                y: trace.y,
                line: { width: 3, color: accentAlt },
              },
        )}
        layout={{
          autosize: true,
          font: { color: textColor },
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          margin: { l: 48, r: 18, t: 22, b: 48 },
          xaxis: { title: axisTitle(plot.xLabel), gridcolor: gridColor, tickfont: { color: textColor } },
          yaxis: { title: axisTitle(plot.yLabel), gridcolor: gridColor, tickfont: { color: textColor } },
          legend: { orientation: "h", font: { color: textColor } },
        }}
        config={{ responsive: true, displaylogo: false }}
        useResizeHandler
      />
    );
  }

  if (plot.kind === "surface3d") {
    return (
      <Plot
        className="plot"
        data={[
          {
            type: "scatter3d",
            mode: "markers",
            name: "data",
            x: plot.scatter.x,
            y: plot.scatter.y,
            z: plot.scatter.z,
            marker: { size: 4, color: accentMain },
          },
          ...(plot.surface.z
            ? [
                {
                  type: "surface",
                  name: "fit",
                  x: plot.surface.x,
                  y: plot.surface.y,
                  z: plot.surface.z,
                  opacity: 0.8,
                  colorscale: "Viridis",
                  showscale: false,
                },
              ]
            : []),
        ]}
        layout={{
          autosize: true,
          font: { color: textColor },
          paper_bgcolor: "transparent",
          margin: { l: 0, r: 0, t: 12, b: 0 },
          scene: {
            xaxis: { title: axisTitle(plot.xLabel), tickfont: { color: textColor }, gridcolor: gridColor },
            yaxis: { title: axisTitle(plot.yLabel), tickfont: { color: textColor }, gridcolor: gridColor },
            zaxis: { title: axisTitle(plot.zLabel), tickfont: { color: textColor }, gridcolor: gridColor },
          },
        }}
        config={{ responsive: true, displaylogo: false }}
        useResizeHandler
      />
    );
  }

  if (plot.kind === "splom") {
    return (
      <Plot
        className="plot"
        data={[
          {
            type: "splom",
            dimensions: plot.dimensions,
            marker: {
              color: accentMain,
              size: 6,
              opacity: 0.75,
            },
          },
        ]}
        layout={{
          autosize: true,
          font: { color: textColor },
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          dragmode: "select",
          margin: { l: 32, r: 12, t: 20, b: 32 },
        }}
        config={{ responsive: true, displaylogo: false }}
        useResizeHandler
      />
    );
  }

  return (
    <Plot
      className="plot"
      data={plot.traces.map((trace) => ({
        type: "scatter",
        mode: trace.mode,
        name: trace.name,
        x: trace.x,
        y: trace.y,
        marker: { size: 7, color: accentMain },
        line: { width: 2, color: "rgba(255,255,255,0.45)", dash: trace.mode === "lines" ? "dash" : "solid" },
      }))}
      layout={{
        autosize: true,
        font: { color: textColor },
        paper_bgcolor: "transparent",
        plot_bgcolor: "transparent",
        margin: { l: 48, r: 18, t: 22, b: 48 },
        xaxis: { title: axisTitle(plot.xLabel), gridcolor: gridColor, tickfont: { color: textColor } },
        yaxis: { title: axisTitle(plot.yLabel), gridcolor: gridColor, tickfont: { color: textColor } },
      }}
      config={{ responsive: true, displaylogo: false }}
      useResizeHandler
    />
  );
}
