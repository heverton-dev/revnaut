/**
 * Hash helpers for route + optional facility tab deep-link.
 * Canonical form: #!/dentgo?f=hubs
 */
export function parseNavHash(hash?: string): { route: string; facility?: string } {
  const raw = (hash ?? (typeof window !== "undefined" ? window.location.hash : "")).replace(
    /^#!?\/?/,
    ""
  );
  const [pathPart, queryPart] = raw.split("?");
  const route = pathPart.trim();
  let facility: string | undefined;
  if (queryPart) {
    const params = new URLSearchParams(queryPart);
    const f = params.get("f");
    if (f && f.trim()) facility = f.trim();
  }
  return { route, facility };
}

export function getInitialFacilityFromHash(): string | undefined {
  if (typeof window === "undefined") return undefined;
  return parseNavHash(window.location.hash).facility;
}

export function buildNavHash(route: string, facility?: string): string {
  if (facility && facility.trim()) {
    return `#!/${route}?f=${encodeURIComponent(facility.trim())}`;
  }
  return `#!/${route}`;
}

export function setNavHash(route: string, facility?: string): void {
  if (typeof window === "undefined") return;
  const next = buildNavHash(route, facility);
  if (window.location.hash !== next) {
    window.location.hash = next;
  }
}
