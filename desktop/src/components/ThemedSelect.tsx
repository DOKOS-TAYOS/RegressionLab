import {
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
  type KeyboardEvent,
} from "react";

type ThemedSelectOption = {
  value: string;
  label: string;
};

type ThemedSelectProps = {
  value: string;
  options: ThemedSelectOption[];
  onChange: (value: string) => void;
  placeholder?: string;
  ariaLabel?: string;
};

export function ThemedSelect({
  value,
  options,
  onChange,
  placeholder,
  ariaLabel,
}: ThemedSelectProps) {
  const rootRef = useRef<HTMLDivElement | null>(null);
  const optionRefs = useRef<Array<HTMLButtonElement | null>>([]);
  const triggerId = useId();
  const listboxId = useId();
  const [open, setOpen] = useState(false);

  const selectedIndex = useMemo(
    () => options.findIndex((option) => option.value === value),
    [options, value],
  );
  const selectedOption = selectedIndex >= 0 ? options[selectedIndex] : null;
  const [highlightedIndex, setHighlightedIndex] = useState(selectedIndex >= 0 ? selectedIndex : 0);

  useEffect(() => {
    setHighlightedIndex(selectedIndex >= 0 ? selectedIndex : 0);
  }, [selectedIndex]);

  useEffect(() => {
    if (!open) {
      return;
    }

    const handlePointerDown = (event: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    };

    document.addEventListener("mousedown", handlePointerDown);
    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
    };
  }, [open]);

  useEffect(() => {
    if (open) {
      optionRefs.current[highlightedIndex]?.focus();
    }
  }, [highlightedIndex, open]);

  const commitSelection = (index: number) => {
    const nextOption = options[index];
    if (!nextOption) {
      return;
    }
    onChange(nextOption.value);
    setOpen(false);
  };

  const moveHighlight = (direction: 1 | -1) => {
    if (options.length === 0) {
      return;
    }
    setHighlightedIndex((current) => {
      const baseIndex = current >= 0 ? current : selectedIndex >= 0 ? selectedIndex : 0;
      const nextIndex = baseIndex + direction;
      if (nextIndex < 0) {
        return options.length - 1;
      }
      if (nextIndex >= options.length) {
        return 0;
      }
      return nextIndex;
    });
  };

  const handleTriggerKeyDown = (event: KeyboardEvent<HTMLButtonElement>) => {
    switch (event.key) {
      case "ArrowDown":
        event.preventDefault();
        setOpen(true);
        setHighlightedIndex(selectedIndex >= 0 ? selectedIndex : 0);
        break;
      case "ArrowUp":
        event.preventDefault();
        setOpen(true);
        setHighlightedIndex(selectedIndex >= 0 ? selectedIndex : Math.max(options.length - 1, 0));
        break;
      case "Enter":
      case " ":
        event.preventDefault();
        setOpen((current) => !current);
        break;
      case "Escape":
        if (open) {
          event.preventDefault();
          setOpen(false);
        }
        break;
      default:
        break;
    }
  };

  const handleListboxKeyDown = (event: KeyboardEvent<HTMLUListElement>) => {
    switch (event.key) {
      case "ArrowDown":
        event.preventDefault();
        moveHighlight(1);
        break;
      case "ArrowUp":
        event.preventDefault();
        moveHighlight(-1);
        break;
      case "Home":
        event.preventDefault();
        setHighlightedIndex(0);
        break;
      case "End":
        event.preventDefault();
        setHighlightedIndex(Math.max(options.length - 1, 0));
        break;
      case "Enter":
      case " ":
        event.preventDefault();
        commitSelection(highlightedIndex);
        break;
      case "Escape":
        event.preventDefault();
        setOpen(false);
        break;
      case "Tab":
        setOpen(false);
        break;
      default:
        break;
    }
  };

  return (
    <div className={`themed-select ${open ? "open" : ""}`} ref={rootRef}>
      <button
        aria-controls={open ? listboxId : undefined}
        aria-expanded={open}
        aria-haspopup="listbox"
        aria-label={ariaLabel}
        className="themed-select-trigger"
        id={triggerId}
        onClick={() => setOpen((current) => !current)}
        onKeyDown={handleTriggerKeyDown}
        type="button"
      >
        <span>{selectedOption?.label ?? placeholder ?? ""}</span>
        <span aria-hidden="true" className="themed-select-caret">
          ▾
        </span>
      </button>

      {open ? (
        <div className="themed-select-popover">
          <ul
            aria-labelledby={triggerId}
            className="themed-select-listbox"
            id={listboxId}
            onKeyDown={handleListboxKeyDown}
            role="listbox"
            tabIndex={-1}
          >
            {options.map((option, index) => {
              const isSelected = option.value === value;
              const isHighlighted = index === highlightedIndex;

              return (
                <li key={option.value} role="presentation">
                  <button
                    aria-selected={isSelected}
                    className={`themed-select-option ${isSelected ? "selected" : ""} ${isHighlighted ? "highlighted" : ""}`}
                    onClick={() => commitSelection(index)}
                    onMouseEnter={() => setHighlightedIndex(index)}
                    ref={(element) => {
                      optionRefs.current[index] = element;
                    }}
                    role="option"
                    type="button"
                  >
                    {option.label}
                  </button>
                </li>
              );
            })}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
