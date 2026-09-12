/** Read Frozen allowlists from Python Core. Adapter must match these. */

export function extractPythonStringSet(source: string, name: string): string[] {
  const match = source.match(
    new RegExp(`${name}\\s*=\\s*frozenset\\(\\s*\\{([^}]*)\\}`, "s"),
  );
  if (!match) {
    throw new Error(`Python constant ${name} not found`);
  }
  return [...match[1].matchAll(/"([^"]+)"/g)].map((item) => item[1]).sort();
}
