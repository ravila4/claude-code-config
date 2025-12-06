# Mermaid Diagram Templates

This document provides reusable templates for common diagram patterns. Copy and adapt these templates for standard use cases.

## Contents

- [System Architecture Template](#system-architecture-template)
- [API Sequence Diagram Template](#api-sequence-diagram-template)
- [Data Flow Pipeline Template](#data-flow-pipeline-template)
- [State Machine Template](#state-machine-template)
- [Decision Tree Template](#decision-tree-template)
- [Microservices Architecture Template](#microservices-architecture-template)
- [CI/CD Pipeline Template](#cicd-pipeline-template)
- [Class Diagram Template](#class-diagram-template)
- [Entity Relationship Template](#entity-relationship-template)
- [Gantt Chart Template](#gantt-chart-template)
- [User Journey Template](#user-journey-template)
- [Template Usage Guidelines](#template-usage-guidelines)

## System Architecture Template

```mermaid
flowchart TB
    subgraph Frontend["Frontend Layer"]
        direction LR
        UI["User Interface"]
        State["State Management"]
        UI --> State
    end

    subgraph Backend["Backend Layer"]
        direction LR
        API["API Server"]
        Cache["Cache"]
        DB["Database"]
        API --> Cache
        API --> DB
    end

    subgraph External["External Services"]
        direction TB
        Auth["Auth Service"]
        Storage["Object Storage"]
    end

    Frontend --> Backend
    Backend --> External

    classDef frontend fill:#f0f4ff,stroke:#9aa4b2,stroke-width:1px,color:#111;
    classDef backend fill:#f8f9fb,stroke:#9aa4b2,stroke-width:1px,color:#111;
    classDef external fill:#eefaf3,stroke:#9aa4b2,stroke-width:1px,color:#111;

    class UI,State frontend
    class API,Cache,DB backend
    class Auth,Storage external
```

## API Sequence Diagram Template

```mermaid
sequenceDiagram
    participant C as Client
    participant G as API Gateway
    participant A as Auth Service
    participant S as Service
    participant D as Database

    C->>G: POST /api/resource
    G->>A: Validate Token
    A-->>G: Token Valid

    G->>S: Process Request
    S->>D: Query Data
    D-->>S: Return Data
    S->>S: Transform Data
    S-->>G: Success Response
    G-->>C: 200 OK

    Note over C,D: Happy path flow
```

## Data Flow Pipeline Template

```mermaid
flowchart LR
    subgraph Ingestion["Data Ingestion"]
        direction TB
        Source["Data Source"]
        Validate["Validation"]
        Source --> Validate
    end

    subgraph Processing["Processing Pipeline"]
        direction TB
        Transform["Transform"]
        Enrich["Enrich"]
        Aggregate["Aggregate"]
        Transform --> Enrich --> Aggregate
    end

    subgraph Storage["Data Storage"]
        direction TB
        Raw["Raw Data Lake"]
        Processed["Processed Data"]
        Analytics["Analytics DB"]
    end

    Ingestion --> Processing
    Processing --> Storage

    classDef input fill:#f0f4ff,stroke:#9aa4b2,stroke-width:1px,color:#111;
    classDef process fill:#f8f9fb,stroke:#9aa4b2,stroke-width:1px,color:#111;
    classDef output fill:#f4f7ff,stroke:#9aa4b2,stroke-width:1px,color:#111;

    class Source,Validate input
    class Transform,Enrich,Aggregate process
    class Raw,Processed,Analytics output
```

## State Machine Template

```mermaid
stateDiagram-v2
    [*] --> Draft: Create

    Draft --> Review: Submit
    Draft --> [*]: Delete

    Review --> Approved: Approve
    Review --> Rejected: Reject
    Review --> Draft: Request Changes

    Rejected --> Draft: Revise
    Rejected --> [*]: Abandon

    Approved --> Published: Publish
    Published --> Archived: Archive

    Archived --> [*]
```

## Decision Tree Template

```mermaid
flowchart TB
    Start["Start Process"]
    Check1{"Condition 1?"}
    Check2{"Condition 2?"}
    Check3{"Condition 3?"}

    ActionA["Action A"]
    ActionB["Action B"]
    ActionC["Action C"]
    ActionD["Action D"]

    Start --> Check1
    Check1 -->|"Yes"| Check2
    Check1 -->|"No"| ActionD

    Check2 -->|"Yes"| ActionA
    Check2 -->|"No"| Check3

    Check3 -->|"Yes"| ActionB
    Check3 -->|"No"| ActionC

    classDef decision fill:#fff7ed,stroke:#fb923c,stroke-width:2px,color:#111;
    classDef action fill:#eefaf3,stroke:#22c55e,stroke-width:1px,color:#111;

    class Check1,Check2,Check3 decision
    class ActionA,ActionB,ActionC,ActionD action
```

## Microservices Architecture Template

```mermaid
flowchart TB
    subgraph Gateway["API Gateway"]
        direction LR
        LB["Load Balancer"]
        Auth["Authentication"]
        LB --> Auth
    end

    subgraph Services["Microservices"]
        direction LR
        UserSvc["User Service"]
        OrderSvc["Order Service"]
        PaymentSvc["Payment Service"]
        NotifySvc["Notification Service"]
    end

    subgraph Data["Data Layer"]
        direction LR
        UserDB["User DB"]
        OrderDB["Order DB"]
        Cache["Redis Cache"]
    end

    subgraph Queue["Message Queue"]
        direction TB
        MQ["RabbitMQ"]
    end

    Gateway --> Services
    UserSvc --> UserDB
    OrderSvc --> OrderDB
    OrderSvc --> Cache
    PaymentSvc --> MQ
    MQ --> NotifySvc

    classDef gateway fill:#f0f4ff,stroke:#9aa4b2,stroke-width:2px,color:#111;
    classDef service fill:#f8f9fb,stroke:#9aa4b2,stroke-width:1px,color:#111;
    classDef data fill:#eefaf3,stroke:#9aa4b2,stroke-width:1px,color:#111;
    classDef message fill:#fff7ed,stroke:#fb923c,stroke-width:1px,color:#111;

    class LB,Auth gateway
    class UserSvc,OrderSvc,PaymentSvc,NotifySvc service
    class UserDB,OrderDB,Cache data
    class MQ message
```

## CI/CD Pipeline Template

```mermaid
flowchart LR
    subgraph Dev["Development"]
        direction TB
        Code["Write Code"]
        Commit["Commit"]
        Code --> Commit
    end

    subgraph CI["Continuous Integration"]
        direction TB
        Build["Build"]
        Test["Run Tests"]
        Lint["Lint & Format"]
        Build --> Test --> Lint
    end

    subgraph CD["Continuous Deployment"]
        direction TB
        Stage["Deploy to Staging"]
        Verify["Verify Staging"]
        Prod["Deploy to Production"]
        Stage --> Verify --> Prod
    end

    Dev --> CI
    CI --> CD

    classDef dev fill:#f0f4ff,stroke:#9aa4b2,stroke-width:1px,color:#111;
    classDef ci fill:#fff7ed,stroke:#fb923c,stroke-width:1px,color:#111;
    classDef cd fill:#eefaf3,stroke:#22c55e,stroke-width:1px,color:#111;

    class Code,Commit dev
    class Build,Test,Lint ci
    class Stage,Verify,Prod cd
```

## Class Diagram Template

```mermaid
classDiagram
    class User {
        +String id
        +String email
        +String name
        +login()
        +logout()
    }

    class Order {
        +String id
        +Date createdAt
        +OrderStatus status
        +addItem()
        +removeItem()
        +calculate()
    }

    class OrderItem {
        +String productId
        +int quantity
        +float price
        +getTotal()
    }

    class Product {
        +String id
        +String name
        +float price
        +int stock
        +updateStock()
    }

    User "1" --> "*" Order : places
    Order "1" --> "*" OrderItem : contains
    OrderItem "*" --> "1" Product : references
```

## Entity Relationship Template

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    USER {
        string id PK
        string email
        string name
        datetime created_at
    }

    ORDER ||--|{ ORDER_ITEM : contains
    ORDER {
        string id PK
        string user_id FK
        datetime created_at
        string status
        float total
    }

    ORDER_ITEM }o--|| PRODUCT : references
    ORDER_ITEM {
        string id PK
        string order_id FK
        string product_id FK
        int quantity
        float price
    }

    PRODUCT {
        string id PK
        string name
        float price
        int stock
    }
```

## Gantt Chart Template

```mermaid
gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    section Planning
        Requirements Gathering :a1, 2024-01-01, 14d
        Design           :a2, after a1, 21d
    section Development
        Backend Development  :b1, after a2, 30d
        Frontend Development :b2, after a2, 30d
        Integration         :b3, after b1, 7d
    section Testing
        QA Testing          :c1, after b3, 14d
        UAT                 :c2, after c1, 7d
    section Deployment
        Production Deploy   :milestone, after c2, 0d
```

## User Journey Template

```mermaid
journey
    title User Shopping Experience
    section Browse
        Visit Homepage: 5: Customer
        Search Products: 4: Customer
        View Product Details: 5: Customer
    section Purchase
        Add to Cart: 4: Customer
        Review Cart: 3: Customer
        Checkout: 2: Customer, System
        Payment: 3: Customer, Payment Gateway
    section Post-Purchase
        Order Confirmation: 5: Customer, System
        Track Shipment: 4: Customer
        Receive Product: 5: Customer
```

## Template Usage Guidelines

### Choosing a Template

1. **System Architecture** - High-level system design, component relationships
2. **API Sequence** - API interactions, request/response flows
3. **Data Flow Pipeline** - ETL processes, data transformation workflows
4. **State Machine** - Entity lifecycle, workflow states
5. **Decision Tree** - Conditional logic, branching processes
6. **Microservices** - Service-oriented architecture, distributed systems
7. **CI/CD Pipeline** - Build and deployment workflows
8. **Class Diagram** - Object-oriented design, class relationships
9. **Entity Relationship** - Database schema, data models
10. **Gantt Chart** - Project timelines, scheduling
11. **User Journey** - User experience flows, interaction mapping

### Customizing Templates

1. **Copy the template** - Start with the closest match
2. **Rename elements** - Update labels to match your domain
3. **Adjust structure** - Add/remove nodes and connections
4. **Apply styling** - Use consistent color palette from syntax guide
5. **Validate syntax** - Check against `syntax_guide.md` rules
6. **Test rendering** - Use validation script to verify

### Color Coding

Use the standard palette for consistency:

- **Input/Sources** - Light blue (#f0f4ff)
- **Processing** - Light gray (#f8f9fb)
- **Calculations** - Light green (#eefaf3)
- **Outputs** - Light purple (#f4f7ff)
- **Warnings/Decisions** - Light orange (#fff7ed)
- **Success** - Green accent (#22c55e)
- **Error** - Red accent (#ef4444)
