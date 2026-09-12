export interface MathSlot {
  id: string;
  display: boolean;
  tex: string;
  closed: boolean;
}

export interface ExtractedMath {
  text: string;
  slots: MathSlot[];
}

export function extractMath(source: string): ExtractedMath {
  const slots: MathSlot[] = [];
  const hold = (display: boolean, tex: string, closed: boolean): string => {
    const id = String(slots.length);
    slots.push({ id, display, tex, closed });
    return display ? `\n\n@@MATH${id}@@\n\n` : `@@MATH${id}@@`;
  };

  let text = source.replace(/\$\$([\s\S]+?)\$\$/g, (_, tex: string) =>
    hold(true, tex, true),
  );
  text = text.replace(/\\\[([\s\S]+?)\\\]/g, (_, tex: string) =>
    hold(true, tex, true),
  );
  text = text.replace(/\\\(([\s\S]+?)\\\)/g, (_, tex: string) =>
    hold(false, tex, true),
  );
  text = text.replace(/(?<!\$)\$(?!\$)([^$\n]+)\$(?!\$)/g, (_, tex: string) =>
    hold(false, tex, true),
  );

  text = text.replace(/\$\$([^$]*)/g, (_, tex: string) => hold(true, tex, false));
  text = text.replace(/\$([^$\n]*)/g, (_, tex: string) => hold(false, tex, false));

  return { text, slots };
}

export function slotToken(id: string): string {
  return `@@MATH${id}@@`;
}
