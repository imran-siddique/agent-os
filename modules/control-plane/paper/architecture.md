graph TD
    User[User / App] -->|Request| Kernel[Agent Kernel]
    Kernel -->|Check| Policy[Policy Engine]
    Kernel -->|Check| Graphs[Constraint Graphs]
    Policy -->|Allow/Deny| Kernel
    Graphs -->|Allow/Deny| Kernel
    Kernel -->|If Denied| Mute[Mute Agent]
    Kernel -->|If Allowed| Sandbox[Execution Engine]
    Mute -->|NULL| User
    Sandbox -->|Action| Resource[Database/API]
    Resource -->|Result| Sandbox
    Sandbox -->|Response| User
    Kernel -.->|Log| Recorder[Flight Recorder]
    style Kernel fill:#f9f,stroke:#333,stroke-width:2px
    style Mute fill:#ff9,stroke:#333
