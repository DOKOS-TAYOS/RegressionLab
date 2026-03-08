import { Fragment } from "react";

function renderInlineMarkdown(text: string) {
  const segments = text.split(/(\*\*[^*]+\*\*)/g).filter(Boolean);

  return segments.map((segment, index) => {
    if (segment.startsWith("**") && segment.endsWith("**")) {
      return <strong key={`strong-${index}`}>{segment.slice(2, -2)}</strong>;
    }
    return <Fragment key={`text-${index}`}>{segment}</Fragment>;
  });
}

export function FormattedText({
  text,
  className,
}: {
  text: string;
  className?: string;
}) {
  const lines = text.split("\n");

  return (
    <>
      {lines.map((line, index) => (
        <p key={`line-${index}`} className={className}>
          {line ? renderInlineMarkdown(line) : "\u00A0"}
        </p>
      ))}
    </>
  );
}
