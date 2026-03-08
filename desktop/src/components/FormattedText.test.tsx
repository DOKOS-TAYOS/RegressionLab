import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { FormattedText } from "@/components/FormattedText";

describe("FormattedText", () => {
  it("renders bold markdown markers as strong text instead of literal asterisks", () => {
    render(<FormattedText text={"Linea con **negrita** y texto final."} />);

    expect(screen.getByText("negrita").tagName).toBe("STRONG");
    expect(screen.getByText(/Linea con/i).textContent).not.toContain("**");
  });

  it("preserves multiple lines as separate paragraphs", () => {
    render(<FormattedText text={"Primera linea\nSegunda linea"} />);

    expect(screen.getByText("Primera linea").tagName).toBe("P");
    expect(screen.getByText("Segunda linea").tagName).toBe("P");
  });
});
