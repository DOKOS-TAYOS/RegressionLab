import { useState } from "react";

import { translate } from "@/i18n";

import { FormattedText } from "./FormattedText";

export function HelpSection({
  headerKey,
  contentKeys,
  language,
  defaultOpen = false,
}: {
  headerKey: string;
  contentKeys: string[];
  language: string;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <article className="accordion">
      <button className="accordion-trigger" onClick={() => setOpen((value) => !value)}>
        <span>{translate(language, headerKey)}</span>
        <span>{open ? "-" : "+"}</span>
      </button>
      {open ? (
        <div className="accordion-body">
          {contentKeys.map((key) => (
            <FormattedText
              key={key}
              text={translate(language, key)}
              className="accordion-paragraph"
            />
          ))}
        </div>
      ) : null}
    </article>
  );
}
