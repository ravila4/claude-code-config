# Graphviz Protocol Contract Templates

This document provides reusable templates for creating protocol contracts, architecture diagrams, and decision-tree specifications using Graphviz DOT language.

## Protocol Contract Template

Protocol contracts are executable specifications that define how agents or systems must behave. Once approved, they become binding implementation contracts.

### Key Principles

1. **Diamond nodes = Decision points** - Explicit branches in reasoning/logic
2. **Subgraphs = Logical phases** - Group related decision sequences
3. **Shape semantics** - Each shape conveys specific meaning (see syntax_guide.md)
4. **Binding contract** - Once approved, this defines required behavior
5. **Completeness** - All decision paths must be explicitly handled

### Basic Protocol Template

```dot
digraph ProtocolName {
  label = "Protocol Name - APPROVED YYYY-MM-DD";
  rankdir = TB;

  // Styling
  node [fontname="Arial", fontsize=11];
  edge [fontname="Arial", fontsize=9];

  // Entry point
  Start [shape=doublecircle, fillcolor=lightblue, style=filled];

  // Decision points
  "Condition met?" [shape=diamond, fillcolor=yellow, style=filled];

  // Actions
  "Execute action A" [shape=box];
  "Execute action B" [shape=box];

  // Exit point
  End [shape=doublecircle, fillcolor=lightgreen, style=filled];

  // Flow
  Start -> "Condition met?";
  "Condition met?" -> "Execute action A" [label="yes"];
  "Condition met?" -> "Execute action B" [label="no"];
  "Execute action A" -> End;
  "Execute action B" -> End;
}
```

### Advanced Protocol with Phases

```dot
digraph AdvancedProtocol {
  label = "Advanced Protocol Contract - APPROVED 2025-10-21";
  rankdir = TB;

  // Styling
  node [fontname="Arial", fontsize=10];
  edge [fontname="Arial", fontsize=9];

  subgraph cluster_entry {
    label = "Entry Point";
    style = filled;
    fillcolor = "#e3f2fd";

    "Event trigger" [shape=ellipse, fillcolor=lightblue, style=filled];
    "Event trigger" -> "First validation?";
  }

  subgraph cluster_validation {
    label = "Validation Phase";
    style = filled;
    fillcolor = "#fff3e0";

    "First validation?" [shape=diamond, fillcolor=yellow, style=filled];
    "Second validation?" [shape=diamond, fillcolor=yellow, style=filled];

    "First validation?" -> "Second validation?" [label="pass"];
    "First validation?" -> "Handle error A" [label="fail"];

    "Second validation?" -> "Process data" [label="pass"];
    "Second validation?" -> "Handle error B" [label="fail"];
  }

  subgraph cluster_processing {
    label = "Processing Phase";
    style = filled;
    fillcolor = "#e8f5e9";

    "Process data" [shape=box];
    "Store results" [shape=box];

    "Process data" -> "Store results";
  }

  subgraph cluster_constraints {
    label = "Constraints & Requirements";
    style = filled;
    fillcolor = "#ffebee";

    "NEVER skip validation" [shape=octagon, fillcolor=red, fontcolor=white, style=filled];
    "MUST log all errors" [shape=note];
  }

  subgraph cluster_exit {
    label = "Exit Point";
    style = filled;
    fillcolor = "#f3e5f5";

    Success [shape=doublecircle, fillcolor=lightgreen, style=filled];
    Failure [shape=doublecircle, fillcolor=pink, style=filled];
  }

  // Flows
  "Handle error A" -> Failure;
  "Handle error B" -> Failure;
  "Store results" -> Success;
}
```

## Agent Protocol Contract Template

Specific template for agent decision-making protocols in the claude-code-agents ecosystem.

```dot
digraph AgentProtocol {
  label = "Agent Behavior Protocol - APPROVED 2025-10-21";
  rankdir = TB;

  node [fontname="Arial", fontsize=10];
  edge [fontname="Arial", fontsize=9];

  // Entry
  Start [shape=doublecircle, label="Task Received"];

  // Confidence check (learning mode trigger)
  "Confidence >= 0.7?" [shape=diamond, fillcolor=yellow, style=filled];

  // High confidence path
  "Execute task" [shape=box, fillcolor=lightgreen, style=filled];
  "Store patterns" [shape=box, fillcolor=lightblue, style=filled];

  // Low confidence path (learning mode)
  "Enter learning mode" [shape=box, fillcolor=orange, style=filled];
  "Ask clarifying questions" [shape=box];
  "Consult memory-keeper" [shape=box];
  "Attempt with explanation" [shape=box];

  // Memory integration
  "Query .memories/" [shape=cylinder, fillcolor=lightyellow];
  "Store to .memories/" [shape=cylinder, fillcolor=lightyellow];

  // Constraints
  subgraph cluster_constraints {
    label = "MUST Requirements";
    style = filled;
    fillcolor = lightyellow;

    "NEVER guess patterns" [shape=octagon, fillcolor=red, fontcolor=white, style=filled];
    "MUST validate before storing" [shape=note];
  }

  // Flows
  Start -> "Query .memories/";
  "Query .memories/" -> "Confidence >= 0.7?";

  "Confidence >= 0.7?" -> "Execute task" [label="yes"];
  "Confidence >= 0.7?" -> "Enter learning mode" [label="no"];

  "Execute task" -> "Store patterns";
  "Store patterns" -> "Store to .memories/";

  "Enter learning mode" -> "Ask clarifying questions";
  "Ask clarifying questions" -> "Consult memory-keeper";
  "Consult memory-keeper" -> "Attempt with explanation";
  "Attempt with explanation" -> "Store to .memories/";
}
```

## Architecture Diagram Template

### Layered Architecture

```dot
digraph LayeredArchitecture {
  label = "Layered System Architecture";
  rankdir = TB;

  node [shape=box, style="rounded,filled", fontname="Arial"];

  // Presentation layer
  { rank=same;
    Web [fillcolor="#e3f2fd", label="Web App"];
    Mobile [fillcolor="#e3f2fd", label="Mobile App"];
  }

  // API layer
  APIGateway [fillcolor="#f3e5f5", label="API Gateway"];

  // Service layer
  { rank=same;
    AuthSvc [fillcolor="#fff3e0", label="Auth Service"];
    UserSvc [fillcolor="#fff3e0", label="User Service"];
    OrderSvc [fillcolor="#fff3e0", label="Order Service"];
  }

  // Data layer
  { rank=same;
    UserDB [shape=cylinder, fillcolor="#ffccbc", label="User DB"];
    OrderDB [shape=cylinder, fillcolor="#ffccbc", label="Order DB"];
    Cache [shape=cylinder, fillcolor="#c8e6c9", label="Redis Cache"];
  }

  // External services
  { rank=same;
    StripeAPI [shape=component, fillcolor="#f8bbd0", label="Stripe API"];
    SendGrid [shape=component, fillcolor="#f8bbd0", label="SendGrid"];
  }

  // Connections
  Web -> APIGateway [label="HTTPS"];
  Mobile -> APIGateway [label="HTTPS"];

  APIGateway -> AuthSvc;
  APIGateway -> UserSvc;
  APIGateway -> OrderSvc;

  AuthSvc -> UserDB;
  UserSvc -> UserDB;
  UserSvc -> Cache;
  OrderSvc -> OrderDB;
  OrderSvc -> StripeAPI [style=dashed];
  OrderSvc -> SendGrid [style=dashed];
}
```

### Microservices Architecture

```dot
digraph Microservices {
  label = "Microservices Architecture";
  rankdir = LR;

  node [fontname="Arial", fontsize=10];

  subgraph cluster_frontend {
    label = "Client Applications";
    style = filled;
    fillcolor = "#e3f2fd";

    Web [shape=box, style="rounded,filled", fillcolor=white];
    Mobile [shape=box, style="rounded,filled", fillcolor=white];
  }

  subgraph cluster_gateway {
    label = "API Gateway";
    style = filled;
    fillcolor = "#f3e5f5";

    Gateway [shape=box, style="rounded,filled", fillcolor=white];
    LoadBalancer [shape=box, style="rounded,filled", fillcolor=white];
  }

  subgraph cluster_services {
    label = "Microservices";
    style = filled;
    fillcolor = "#fff3e0";

    UserService [shape=box, style="rounded,filled", fillcolor=white];
    OrderService [shape=box, style="rounded,filled", fillcolor=white];
    PaymentService [shape=box, style="rounded,filled", fillcolor=white];
    NotificationService [shape=box, style="rounded,filled", fillcolor=white];
  }

  subgraph cluster_data {
    label = "Data Layer";
    style = filled;
    fillcolor = "#ffccbc";

    UserDB [shape=cylinder, fillcolor=white];
    OrderDB [shape=cylinder, fillcolor=white];
    Cache [shape=cylinder, fillcolor=white];
  }

  subgraph cluster_messaging {
    label = "Message Queue";
    style = filled;
    fillcolor = "#c8e6c9";

    RabbitMQ [shape=box, style="rounded,filled", fillcolor=white];
  }

  // Connections
  Web -> LoadBalancer;
  Mobile -> LoadBalancer;
  LoadBalancer -> Gateway;

  Gateway -> UserService;
  Gateway -> OrderService;
  Gateway -> PaymentService;

  UserService -> UserDB;
  OrderService -> OrderDB;
  OrderService -> Cache;

  PaymentService -> RabbitMQ [style=dotted, label="publish"];
  RabbitMQ -> NotificationService [style=dotted, label="subscribe"];
}
```

## Dependency Graph Template

```dot
digraph DependencyGraph {
  label = "Module Dependency Graph";
  rankdir = LR;

  node [shape=folder, style=filled, fillcolor=lightgray, fontname="Arial"];

  // Core modules
  Core [fillcolor=lightblue];
  Utils [fillcolor=lightblue];

  // Feature modules
  Auth [fillcolor=lightgreen];
  Users [fillcolor=lightgreen];
  Orders [fillcolor=lightgreen];
  Payments [fillcolor=lightgreen];

  // UI modules
  WebUI [fillcolor=lightyellow];
  MobileUI [fillcolor=lightyellow];

  // Dependencies
  Auth -> Core;
  Auth -> Utils;

  Users -> Core;
  Users -> Utils;
  Users -> Auth [style=dashed, label="optional"];

  Orders -> Core;
  Orders -> Users;
  Orders -> Utils;

  Payments -> Core;
  Payments -> Orders;
  Payments -> Utils;

  WebUI -> Auth;
  WebUI -> Users;
  WebUI -> Orders;
  WebUI -> Payments;

  MobileUI -> Auth;
  MobileUI -> Users;
  MobileUI -> Orders;

  // Legend
  subgraph cluster_legend {
    label = "Legend";
    style = filled;
    fillcolor = white;

    LCore [label="Core", fillcolor=lightblue];
    LFeature [label="Feature", fillcolor=lightgreen];
    LUI [label="UI", fillcolor=lightyellow];

    LCore -> LFeature [style=invis];
    LFeature -> LUI [style=invis];
  }
}
```

## Decision Tree Template

```dot
digraph DecisionTree {
  label = "CI/CD Pipeline Decision Tree";
  rankdir = TB;

  node [fontname="Arial", fontsize=10];

  // Start
  Start [shape=ellipse, fillcolor=lightblue, style=filled, label="Code Pushed"];

  // Decisions
  "Tests passing?" [shape=diamond, fillcolor=yellow, style=filled];
  "On main branch?" [shape=diamond, fillcolor=yellow, style=filled];
  "All checks pass?" [shape=diamond, fillcolor=yellow, style=filled];

  // Actions
  "Run tests" [shape=box];
  "Notify failure" [shape=box, fillcolor=pink, style=filled];
  "Build artifact" [shape=box];
  "Deploy to staging" [shape=box];
  "Run integration tests" [shape=box];
  "Deploy to production" [shape=box];

  // End states
  Success [shape=doublecircle, fillcolor=lightgreen, style=filled];
  Failure [shape=doublecircle, fillcolor=pink, style=filled];

  // Constraints
  "NEVER deploy failing tests" [shape=octagon, fillcolor=red, fontcolor=white, style=filled];

  // Flow
  Start -> "Run tests";
  "Run tests" -> "Tests passing?";

  "Tests passing?" -> "On main branch?" [label="yes"];
  "Tests passing?" -> "Notify failure" [label="no"];
  "Notify failure" -> Failure;

  "On main branch?" -> "Build artifact" [label="yes"];
  "On main branch?" -> Success [label="no", xlabel="PR only"];

  "Build artifact" -> "Deploy to staging";
  "Deploy to staging" -> "Run integration tests";
  "Run integration tests" -> "All checks pass?";

  "All checks pass?" -> "Deploy to production" [label="yes"];
  "All checks pass?" -> "Notify failure" [label="no"];

  "Deploy to production" -> Success;
}
```

## State Machine Template

```dot
digraph StateMachine {
  label = "Order State Machine";
  rankdir = LR;

  node [shape=ellipse, style=filled, fontname="Arial"];

  // States
  Draft [fillcolor=lightgray];
  Submitted [fillcolor=lightyellow];
  Approved [fillcolor=lightgreen];
  Processing [fillcolor=lightblue];
  Shipped [fillcolor=lightcyan];
  Delivered [fillcolor=green, fontcolor=white];
  Cancelled [fillcolor=red, fontcolor=white];

  // Transitions
  Draft -> Submitted [label="submit"];
  Submitted -> Draft [label="withdraw"];
  Submitted -> Approved [label="approve"];
  Submitted -> Cancelled [label="reject"];

  Approved -> Processing [label="start_processing"];
  Processing -> Shipped [label="ship"];
  Shipped -> Delivered [label="confirm_delivery"];

  // Cancellation paths
  Approved -> Cancelled [label="cancel"];
  Processing -> Cancelled [label="cancel"];
}
```

## Integration Workflow Template

For claude-code-agents ecosystem - showing agent collaboration:

```dot
digraph AgentWorkflow {
  label = "Multi-Agent Collaboration Workflow";
  rankdir = TB;

  node [fontname="Arial", fontsize=10];

  // User interaction
  User [shape=ellipse, fillcolor=lightblue, style=filled];

  // Agents
  SoftwareArchitect [shape=box, style="rounded,filled", fillcolor="#f3e5f5"];
  GraphvizArchitect [shape=box, style="rounded,filled", fillcolor="#e3f2fd"];
  MermaidExpert [shape=box, style="rounded,filled", fillcolor="#fff3e0"];
  MemoryKeeper [shape=box, style="rounded,filled", fillcolor="#c8e6c9"];

  // Skills
  GraphvizSkill [shape=box, fillcolor=lightgray, label="graphviz-diagrams\n(skill)"];
  MermaidSkill [shape=box, fillcolor=lightgray, label="mermaid-diagrams\n(skill)"];

  // Workflow
  User -> SoftwareArchitect [label="1. Request architecture"];

  SoftwareArchitect -> MemoryKeeper [label="2. Query patterns"];
  MemoryKeeper -> SoftwareArchitect [label="3. Return patterns"];

  SoftwareArchitect -> GraphvizArchitect [label="4. Request system diagram"];
  GraphvizArchitect -> GraphvizSkill [label="5. Use skill", style=dashed];
  GraphvizSkill -> GraphvizArchitect [label="6. DOT diagram", style=dashed];

  SoftwareArchitect -> MermaidExpert [label="7. Request sequence diagram"];
  MermaidExpert -> MermaidSkill [label="8. Use skill", style=dashed];
  MermaidSkill -> MermaidExpert [label="9. Mermaid diagram", style=dashed];

  GraphvizArchitect -> SoftwareArchitect [label="10. Return diagram"];
  MermaidExpert -> SoftwareArchitect [label="11. Return diagram"];

  SoftwareArchitect -> User [label="12. Complete proposal"];

  User -> MemoryKeeper [label="13. Store successful pattern"];
}
```

## Template Usage Guidelines

### Choosing a Template

1. **Protocol Contract** - Binding decision-tree specifications for agent/system behavior
2. **Agent Protocol** - Learning mode, confidence thresholds, memory integration
3. **Layered Architecture** - Traditional tiered systems (presentation → business → data)
4. **Microservices** - Distributed services with message queues and async communication
5. **Dependency Graph** - Module/package dependencies, build order
6. **Decision Tree** - Workflow automation, approval processes
7. **State Machine** - Entity lifecycle, status transitions
8. **Integration Workflow** - Multi-agent/multi-system collaboration

### Customizing Templates

1. **Copy the template** - Start with the closest match
2. **Update labels** - Replace placeholder names with your domain terms
3. **Adjust structure** - Add/remove nodes and edges as needed
4. **Apply styling** - Use consistent colors from syntax_guide.md
5. **Add metadata** - Include approval date, version, purpose in label
6. **Validate syntax** - Use validation script before finalizing
7. **Test layout** - Try different engines if default doesn't work well

### Protocol Contract Workflow

1. **Design phase** - Create protocol diagram from requirements
2. **Review phase** - Stakeholders review and request changes
3. **Approval phase** - Add approval date to diagram label
4. **Storage phase** - Save to `.claude/protocols/[name].dot`
5. **Implementation phase** - Implementing agents reference protocol
6. **Validation phase** - Verify implementation matches protocol

### Protocol Implementation Contract

When a protocol is approved, implementing agents receive:

```markdown
BEFORE writing code, review: .claude/protocols/protocol-name.dot

This diagram is the APPROVED architecture contract. Your implementation MUST:
✓ Follow every decision path shown
✓ Handle all diamond (decision) nodes explicitly
✓ Implement all error paths
✓ Respect all octagon (NEVER) constraints
✓ Implement all note (MUST) requirements

Any deviation requires architecture review and approval.
```

## Best Practices

1. **Be complete** - Show all decision paths, no implicit branches
2. **Use semantic shapes** - Follow shape conventions consistently
3. **Label clearly** - Every edge from a diamond must have a label
4. **Group logically** - Use subgraphs for phases or components
5. **Highlight constraints** - Use octagon shapes for NEVER/MUST NOT rules
6. **Document requirements** - Use note shapes for MUST requirements
7. **Version contracts** - Include approval date in diagram label
8. **Test rendering** - Validate before presenting
9. **Store protocols** - Save approved protocols for reference
10. **Enforce contracts** - Reference protocols during implementation
