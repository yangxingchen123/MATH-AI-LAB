import type { ResearchActor } from "./actor.ts";

export interface SessionAction {
  actor: ResearchActor;
  kind: string;
  description: string;
  timestamp: string;
}

export interface ResearchSession {
  id: string;
  researcher: ResearchActor;
  goal: string;
  inputs: string[];
  actions: SessionAction[];
  outputs: string[];
  events: string[];
  conclusion?: string;
}

export function createSession(
  input: Omit<ResearchSession, "actions" | "outputs" | "events"> &
    Partial<Pick<ResearchSession, "actions" | "outputs" | "events">>,
): { ok: true; session: ResearchSession } | { ok: false; error: string } {
  if (!input.id?.trim() || !input.goal?.trim()) {
    return { ok: false, error: "ResearchSession requires id and goal." };
  }
  if (!input.researcher?.type || !input.researcher.id?.trim()) {
    return { ok: false, error: "ResearchSession requires researcher." };
  }
  return {
    ok: true,
    session: {
      id: input.id,
      researcher: input.researcher,
      goal: input.goal,
      inputs: input.inputs ?? [],
      actions: input.actions ?? [],
      outputs: input.outputs ?? [],
      events: input.events ?? [],
      conclusion: input.conclusion,
    },
  };
}

export function recordSessionAction(
  session: ResearchSession,
  action: SessionAction,
): { ok: true; session: ResearchSession } | { ok: false; error: string } {
  if (!action.actor?.type || !action.description?.trim() || !action.kind?.trim()) {
    return { ok: false, error: "Session action requires actor, kind, and description." };
  }
  return { ok: true, session: { ...session, actions: [...session.actions, action] } };
}

export function concludeSession(session: ResearchSession, conclusion: string): ResearchSession {
  return { ...session, conclusion };
}

export function sessionConclusionIsTheorem(_session: ResearchSession): false {
  return false;
}
