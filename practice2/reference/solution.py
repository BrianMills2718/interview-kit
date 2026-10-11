"""Reference solution. Do not open it during a practice run; it exists so tests can prove the grader passes and fails."""

import ipaddress
from typing import Literal

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt
from pydantic import BaseModel, Field, model_validator

SEARCH_LIMIT = 4
INTERNAL = ipaddress.ip_network("10.0.0.0/8")


class Verdict(BaseModel):
    """Final triage verdict."""

    severity: Literal["low", "medium", "high", "critical"]
    host: str | None = Field(default=None, pattern=r"^[a-z0-9-]+$")
    action: str = Field(description="what was done or should be done, in one sentence")
    evidence: list[str] = Field(default_factory=list, description="log ids such as L-3")

    @model_validator(mode="after")
    def serious_needs_evidence(self):
        if any(not e.startswith("L-") or not e[2:].isdigit() for e in self.evidence):
            raise ValueError("evidence ids look like L-3")
        if self.severity in ("high", "critical") and not self.evidence:
            raise ValueError("high or critical needs at least one evidence log id")
        return self


def build_agent(llm, soc):
    hosts = soc["hosts"]
    searches = {"n": 0}

    @tool
    def get_host(name: str) -> str:
        """Look up a host by name, e.g. web-1 (case does not matter)."""
        h = hosts.get(name.lower())
        if not h:
            return f"Host {name} not found."
        return f"{name.lower()}: {h['env']}, owner {h['owner']}, ip {h['ip']}"

    @tool
    def search_logs(host: str, term: str) -> str:
        """Search one host's logs for a term (case-insensitive); newest first, at most 3 lines."""
        searches["n"] += 1
        if searches["n"] > SEARCH_LIMIT:
            return f"Search limit reached ({SEARCH_LIMIT})."
        if host.lower() not in hosts:
            return f"Host {host} not found."
        hits = [l for l in soc["logs"] if l["host"] == host.lower() and term.lower() in l["text"].lower()]
        hits = sorted(hits, key=lambda l: l["ts"], reverse=True)[:3]
        return "\n".join(f"{l['id']} {l['ts']} {l['text']}" for l in hits) or "No matching logs."

    @tool
    def block_ip(ip: str, reason: str) -> str:
        """Block an IP address at the firewall. Unknown IPs wait for a human reviewer."""
        try:
            addr = ipaddress.IPv4Address(ip)
        except ValueError:
            return f"Invalid IP: {ip}."
        if addr in INTERNAL:
            return f"Refused: {ip} is internal."
        if ip in soc["blocked"]:
            return f"{ip} is already blocked."
        if ip in soc["known_bad"]:
            soc["blocked"].append(ip)
            return f"Blocked {ip} (known bad)."
        answer = interrupt({"ip": ip, "reason": reason})
        if str(answer).strip().lower() != "yes":
            return f"Block of {ip} declined by reviewer."
        soc["blocked"].append(ip)
        return f"Blocked {ip} after approval."

    return create_agent(llm, tools=[get_host, search_logs, block_ip],
                        response_format=ToolStrategy(Verdict), checkpointer=InMemorySaver(),
                        system_prompt="You are a security triage agent. Look before you act; cite the log ids you relied on.")
