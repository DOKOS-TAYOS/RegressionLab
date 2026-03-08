import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ThemedSelect } from "@/components/ThemedSelect";

describe("ThemedSelect", () => {
  it("closes the option list after selecting an item with the mouse", () => {
    let currentValue = "";

    const { rerender } = render(
      <ThemedSelect
        ariaLabel="Equation select"
        onChange={(value) => {
          currentValue = value;
          rerender(
            <ThemedSelect
              ariaLabel="Equation select"
              onChange={(nextValue) => {
                currentValue = nextValue;
              }}
              options={[
                { value: "line", label: "Linear" },
                { value: "quad", label: "Quadratic" },
              ]}
              value={currentValue}
            />,
          );
        }}
        options={[
          { value: "line", label: "Linear" },
          { value: "quad", label: "Quadratic" },
        ]}
        value={currentValue}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "Equation select" }));
    expect(screen.getByRole("listbox")).toBeTruthy();

    fireEvent.mouseDown(screen.getByRole("option", { name: "Quadratic" }));

    expect(screen.queryByRole("listbox")).toBeNull();
  });
});
