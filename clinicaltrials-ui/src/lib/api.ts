export interface ThinkingStep {
  [key: string]: any;
}

export interface QueryRequest {
  query: string;
  session_id?: string;
}

export interface QueryResponse {
  response: string;
  session_id: string;
  thinking_steps: ThinkingStep[];
}

export interface SessionResponse {
  session_id: string;
  message_count: number;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export class TrialAgentAPI {
  static async healthCheck() {
    const res = await fetch(`${API_BASE_URL}/health`);
    return res.json();
  }

  static async query(request: QueryRequest): Promise<QueryResponse> {
    const res = await fetch(`${API_BASE_URL}/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });
    if (!res.ok) {
      throw new Error("Failed to process query");
    }
    return res.json();
  }

  static async deleteSession(sessionId: string) {
    const res = await fetch(`${API_BASE_URL}/sessions/${sessionId}`, {
      method: "DELETE",
    });
    return res.json();
  }

  static async getSession(sessionId: string): Promise<SessionResponse> {
    const res = await fetch(`${API_BASE_URL}/sessions/${sessionId}`);
    if (!res.ok) {
      throw new Error("Failed to get session");
    }
    return res.json();
  }

  static getStreamUrl(sessionId: string, query: string) {
    const url = new URL(`${API_BASE_URL}/stream/${sessionId}`);
    url.searchParams.append("query", query);
    return url.toString();
  }
}
