# System model

## Goals
- Outcome: an analyst sends an alert and gets a validated `Verdict`; outside IPs are blocked only by rule or with a reviewer's yes.
- Quality goals: correct blocks, bounded searches, validated final answer.

## 1. Context: who and what is outside the system?
```mermaid
flowchart LR
  Analyst -->|alert text| Agent
  Agent -->|tool-calling prompts| LLM
  Agent -->|approval question| Reviewer
  Agent -->|reads and appends| SOC[soc dict: hosts, logs, known_bad, blocked]
```

## 2. Building blocks: which part owns what?
```mermaid
flowchart TB
  build_agent["build_agent()"] --> make_tools["make_tools()"]
  build_agent --> Verdict
  make_tools --> check_and_block["check_and_block()"]
  check_and_block --> is_yes["is_yes()"]
```

| Block | Owns | Code |
|---|---|---|
| graph | agent loop, checkpointer, structured output | `build_agent()` |
| tools | host lookup, log search, search counter | `make_tools()` |
| block rules | the five ordered rules and the pause | `check_and_block()` |
| final answer | validation | `Verdict` |

## 3. Main sequence: what happens, in order, on the main path?
```mermaid
sequenceDiagram
  participant Caller
  participant Graph
  participant Tools
  participant Reviewer
  Caller->>Graph: invoke(messages)
  Graph->>Tools: get_host, search_logs
  Graph->>Tools: block_ip
  Tools-->>Caller: __interrupt__
  Caller->>Graph: Command(resume="yes")
  Graph->>Tools: block_ip resumes, appends IP
  Graph-->>Caller: structured_response Verdict
```

## 4. Rules: in what order are the business rules checked?
```mermaid
flowchart TD
  A{IPv4?} -->|no| I[Invalid IP]
  A -->|yes| B{in 10/8?}
  B -->|yes| R[Refused internal]
  B -->|no| C{already blocked?}
  C -->|yes| AB[already blocked]
  C -->|no| D{known bad?}
  D -->|yes| KB[Blocked known bad]
  D -->|no| E{reviewer says yes?}
  E -->|yes| OK[Blocked after approval]
  E -->|no| DEC[Declined]
```

## 5. States: what states does the main item move through?
```mermaid
stateDiagram-v2
  [*] --> Requested
  Requested --> Rejected: invalid, internal or already blocked
  Requested --> Blocked: known bad
  Requested --> AwaitingReview: unknown outside IP
  AwaitingReview --> Blocked: yes
  AwaitingReview --> Declined: anything else
```

## 6. Data: what are the typed contracts and state?
```mermaid
classDiagram
  class Verdict {
    severity: low|medium|high|critical
    host: str lower case or None
    action: str one sentence
    evidence: list of L-n ids
  }
```

## Runtime: which function writes each record?
| Process | Trigger | Reads | Writes | Writer |
|---|---|---|---|---|
| block | block_ip tool call | soc blocked, known_bad | soc["blocked"] | `check_and_block()` |
| search count | search_logs call | counter | counter | `make_tools()` |

## Contracts: what crosses between parts, and how it fails
| Crossing | Producer | Consumer | Shape | On failure |
|---|---|---|---|---|
| final answer | LLM | caller | `Verdict` | validation error back to the LLM |
| approval | caller | block_ip | resume string | anything but yes declines |

## Quality: what observable result shows each goal holds?
| Goal | Observable pattern | Test |
|---|---|---|
| correct blocks | only rule 4 or a yes appends | `test_block_rule5_pauses_for_reviewer` |
| bounded searches | 5th call returns the limit text | `test_search_limit_counts_every_call_including_unknown_hosts` |
| validated answer | bad Verdict retried | `test_invalid_verdict_goes_back_for_retry` |

## Unknowns
| Unknown | What would decide it |
|---|---|
| two unknown-IP blocks in one turn give two pending interrupts; a plain resume then fails | a case with two reviewer pauses in one turn |
