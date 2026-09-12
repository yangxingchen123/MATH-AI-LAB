export interface ResearchSpace {
  id: string;
  title: string;
  origin: "knowledge_domain" | "research_project" | "unclassified";
  entityIds: string[];
}
