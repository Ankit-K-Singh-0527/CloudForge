CloudForge — Database Schema & Architecture
Document Type: Technical Architecture Documentation
Project: CloudForge
Database: PostgreSQL (Neon)
ORM: SQLAlchemy
Migration Tool: Flask-Migrate / Alembic
Schema Status: Approved Design — Implementation Pending
1. Overview
CloudForge uses a relational database architecture built around user identity, workspace ownership, project management, authorization, and audit logging.

The initial schema contains seven core entities:
1. users
2. user_credentials
3. user_identities
4. workspaces
5. workspace_memberships
6. projects
7. audit_events
The design supports multi-user collaboration, workspace-level authorization, project isolation, multiple sign-in methods, and auditable operations.
1.1 Authentication model
CloudForge uses a hybrid authentication architecture:
- Google sign-in: Google OpenID Connect authenticates the external Google account. The Flask backend verifies the Google identity token and resolves the identity to a CloudForge user.
- Email/password sign-in: CloudForge manages email/password authentication in Flask. Passwords are hashed using Argon2id.
- One CloudForge account: Both methods resolve to the same users record. A user may have a Google identity, a password credential, or both.
- CloudForge-owned authorization: Google establishes external identity only. CloudForge remains responsible for sessions, workspace membership, roles, project permissions, and audit history.
- Extensible providers: The schema supports additional external identity providers, such as GitHub, without changing the central user model.
Firebase Authentication is not required for the approved initial architecture. It may be evaluated later as an alternative identity broker, but it is not part of the initial implementation.
1.2 Technology stack
Component	Technology
Database	PostgreSQL
Hosting	Neon
ORM	SQLAlchemy
Migration management	Flask-Migrate
Migration engine	Alembic
Primary keys	UUID
Structured metadata	PostgreSQL JSONB
Backend	Python / Flask
Google authentication	Google OAuth 2.0 / OpenID Connect
Email/password hashing	Argon2id
Browser authentication	Flask-managed secure session cookies
CLI authentication	Separate short-lived token/device authorization strategy


2. Entity Relationship Diagram (ERD)
The diagram represents the approved initial database design.
```mermaid
erDiagram
    USERS ||--o| USER_CREDENTIALS : has
    USERS ||--o{ USER_IDENTITIES : links
    USERS ||--o{ WORKSPACE_MEMBERSHIPS : joins
    WORKSPACES ||--o{ WORKSPACE_MEMBERSHIPS : contains
    WORKSPACES ||--o{ PROJECTS : owns
    USERS ||--o{ PROJECTS : creates
    USERS ||--o{ AUDIT_EVENTS : performs
    WORKSPACES ||--o{ AUDIT_EVENTS : records

    USERS {
        UUID id PK
        VARCHAR email UK
        VARCHAR full_name
        BOOLEAN is_active
        TIMESTAMPTZ email_verified_at
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }

    USER_CREDENTIALS {
        UUID id PK
        UUID user_id FK UK
        VARCHAR password_hash
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }

    USER_IDENTITIES {
        UUID id PK
        UUID user_id FK
        VARCHAR provider
        VARCHAR provider_user_id
        VARCHAR provider_email
        TIMESTAMPTZ created_at
    }

    WORKSPACES {
        UUID id PK
        VARCHAR name
        VARCHAR slug UK
        VARCHAR kind
        UUID created_by FK
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }

    WORKSPACE_MEMBERSHIPS {
        UUID id PK
        UUID user_id FK
        UUID workspace_id FK
        VARCHAR role
        TIMESTAMPTZ joined_at
    }

    PROJECTS {
        UUID id PK
        UUID workspace_id FK
        UUID created_by FK
        VARCHAR name
        VARCHAR slug
        TEXT description
        VARCHAR status
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }

    AUDIT_EVENTS {
        UUID id PK
        UUID actor_user_id FK
        UUID workspace_id FK
        VARCHAR action
        VARCHAR resource_type
        UUID resource_id
        JSONB metadata
        TIMESTAMPTZ created_at
    }
```
2.1 Relationship explanation
Relationship	Cardinality	Description
Users → User Credentials	One-to-One (optional)	A user may have one CloudForge password credential, or none if Google-only.
Users → User Identities	One-to-Many	A user can link external identities from one or more providers.
Users → Workspace Memberships	One-to-Many	A user can join multiple workspaces.
Workspaces → Workspace Memberships	One-to-Many	A workspace can contain multiple users.
Workspaces → Projects	One-to-Many	A workspace can own multiple projects.
Users → Projects	One-to-Many	A user can create multiple projects.
Users → Audit Events	One-to-Many	A user can perform multiple recorded actions.
Workspaces → Audit Events	One-to-Many	A workspace can contain multiple audit records.


The workspace_memberships table establishes a many-to-many relationship between users and workspaces. user_credentials stores an optional one-to-one password credential, while user_identities stores external provider identities linked to a CloudForge user.
3. Table Specifications
3.1 Users
Table: users

Stores the canonical CloudForge account profile. A user exists independently of the authentication method used to sign in. Password credentials and external provider identities are stored separately.
Column	PostgreSQL Type	Constraints
id	UUID	Primary Key
email	VARCHAR(320)	Not Null; case-insensitive unique
full_name	VARCHAR(120)	Not Null
is_active	BOOLEAN	Not Null, Default TRUE
email_verified_at	TIMESTAMPTZ	Nullable
created_at	TIMESTAMPTZ	Not Null
updated_at	TIMESTAMPTZ	Not Null


Design decisions:
- Normalize email addresses before storage.
- Enforce case-insensitive email uniqueness.
- Do not put provider-specific credentials or password hashes in the users table.
- A user may authenticate with Google, email/password, or both.
- Use UUID identifiers.
- Preserve historical audit information when accounts are deactivated.
- A verified email address is required before using an external provider email for account discovery or account linking.
3.2 User Credentials
Table: user_credentials

Stores the optional password credential for accounts that use CloudForge-managed email/password authentication.
Column	PostgreSQL Type	Constraints
id	UUID	Primary Key
user_id	UUID	Foreign Key → users.id; Unique, Not Null
password_hash	VARCHAR(255)	Not Null
created_at	TIMESTAMPTZ	Not Null
updated_at	TIMESTAMPTZ	Not Null


Design decisions:
- Store only an Argon2id password hash; never store plaintext passwords.
- This table is optional for a user. Google-only accounts do not need a credential row.
- Enforce at most one password credential per user with a unique constraint on user_id.
- Password changes update the hash and updated_at; they do not change the user's identity.
- Password reset tokens, if introduced, must be stored separately as securely hashed, expiring tokens. They are not part of this initial schema.
3.3 User Identities
Table: user_identities

Maps a CloudForge user to an external identity provider account. Google is the first supported provider. The table is designed to support additional providers, such as GitHub, later.
Column	PostgreSQL Type	Constraints
id	UUID	Primary Key
user_id	UUID	Foreign Key → users.id; Not Null
provider	VARCHAR(30)	Not Null
provider_user_id	VARCHAR(255)	Not Null
provider_email	VARCHAR(320)	Nullable
created_at	TIMESTAMPTZ	Not Null


Constraints and indexes:
- Unique (provider, provider_user_id) so one external provider identity cannot be attached to multiple CloudForge users.
- Index user_id to retrieve all identities linked to an account.
- Provider values are normalized lowercase identifiers; initially, google.
- provider_user_id stores Google's stable OpenID Connect sub claim, not an email address.
- provider_email is informational and must not be treated as the stable identity key.
Design decisions:
- Verify Google identity tokens on the Flask backend using a supported verification library/process.
- Validate the token signature, issuer, audience, expiry, and the OAuth flow's state and nonce protections.
- Use the verified sub claim as the Google identity key.
- Require a verified provider email before using it for account discovery or linking.
- Do not silently link accounts solely because email strings match. Account linking must require an authenticated, safe linking flow or an explicitly approved and verified first-login policy.
- Never store Google access tokens, refresh tokens, ID tokens, client secrets, or other provider secrets in this table.
- If future provider API access requires token storage, design a dedicated encrypted credential store rather than adding plaintext tokens here.
3.4 Workspaces
Table: workspaces

Represents an organizational boundary for projects and resources.
Column	PostgreSQL Type	Constraints
id	UUID	Primary Key
name	VARCHAR(120)	Not Null
slug	VARCHAR(120)	Unique, Not Null
kind	VARCHAR(20)	Not Null
created_by	UUID	Foreign Key → users.id
created_at	TIMESTAMPTZ	Not Null
updated_at	TIMESTAMPTZ	Not Null


Workspace kinds:
- personal
- team
Design decisions:
- Automatically create a personal workspace during either email/password or Google-based user registration.
- Assign its creator the owner role.
- A user can have only one personal workspace.
- Support multiple team workspaces.
- Workspace slugs must be globally unique.
3.5 Workspace Memberships
Table: workspace_memberships

Connects users to workspaces and defines their access roles.
Column	PostgreSQL Type	Constraints
id	UUID	Primary Key
user_id	UUID	Foreign Key → users.id
workspace_id	UUID	Foreign Key → workspaces.id
role	VARCHAR(20)	Not Null
joined_at	TIMESTAMPTZ	Not Null


Approved roles:
Role	Responsibility
owner	Full workspace control
admin	Manage members and projects
developer	Create and manage projects and deployments
viewer	Read-only access


Constraints:
- Unique (user_id, workspace_id).
- Role must belong to the approved role set.
- Index user_id.
- Index workspace_id.
3.6 Projects
Table: projects

Stores projects managed inside CloudForge workspaces.
Column	PostgreSQL Type	Constraints
id	UUID	Primary Key
workspace_id	UUID	Foreign Key → workspaces.id
created_by	UUID	Foreign Key → users.id
name	VARCHAR(120)	Not Null
slug	VARCHAR(120)	Not Null
description	TEXT	Nullable
status	VARCHAR(20)	Not Null, Default active
created_at	TIMESTAMPTZ	Not Null
updated_at	TIMESTAMPTZ	Not Null


Project statuses:
- active
- archived
Constraints:
- Unique (workspace_id, slug).
- Index workspace_id.
- Index created_by.
Archival strategy:

Projects will be archived rather than permanently deleted in the initial implementation. This preserves project identity and provides a foundation for retaining future deployment history.
3.7 Audit Events
Table: audit_events

Stores important actions performed by users or the CloudForge system.
Column	PostgreSQL Type	Constraints
id	UUID	Primary Key
actor_user_id	UUID	Nullable Foreign Key → users.id
workspace_id	UUID	Nullable Foreign Key → workspaces.id
action	VARCHAR(100)	Not Null
resource_type	VARCHAR(50)	Not Null
resource_id	UUID	Nullable
metadata	JSONB	Not Null, Default empty object
created_at	TIMESTAMPTZ	Not Null


Example actions:
Action	Resource
user.registered	User
user.login_succeeded	User
user.login_failed	User
user.identity_linked	User
workspace.created	Workspace
member.invited	Workspace
project.created	Project
project.archived	Project
deployment.started	Deployment
infrastructure.destroyed	Infrastructure


The last two examples anticipate future CloudForge functionality.

Design decisions:
- Use JSONB for flexible event metadata.
- Preserve historical audit records.
- Treat audit events as append-only through normal application operations.
- Never store passwords, session tokens, OAuth tokens, client secrets, or cloud credentials in audit metadata.
- Avoid logging raw authentication tokens or sensitive provider responses.
4. Database Constraints and Indexes
Table	Constraint / Index	Purpose
users	Unique normalized email (case-insensitive)	Prevent duplicate CloudForge accounts
user_credentials	Unique user_id	At most one password credential per user
user_identities	Unique provider + provider_user_id	Prevent one external identity being linked to multiple users
user_identities	Index user_id	Retrieve authentication providers linked to a user
workspaces	Unique slug	Prevent duplicate workspace identifiers
workspaces	Partial unique index on personal workspace creator	One personal workspace per user
workspace_memberships	Unique user_id + workspace_id	Prevent duplicate memberships
workspace_memberships	Index user_id	Retrieve user workspaces
workspace_memberships	Index workspace_id	Retrieve workspace members
projects	Unique workspace_id + slug	Prevent duplicate project slugs within a workspace
projects	Index workspace_id	Retrieve workspace projects
projects	Index created_by	Retrieve projects by creator
audit_events	Composite index workspace_id + created_at	Retrieve workspace activity
audit_events	Composite index actor_user_id + created_at	Retrieve user activity


Primary keys and unique constraints already create their own indexes in PostgreSQL. Avoid adding redundant indexes.
5. Referential Integrity and Deletion Policies
CloudForge will avoid uncontrolled cascading deletion.
Relationship	Policy
User → Password credential	Handle through explicit account lifecycle operations
User → External identity	Handle through explicit account lifecycle operations
User → Workspace creator	Restrict deletion or require ownership reassignment
User → Membership	Handle eligible memberships explicitly
Workspace → Membership	Restrict deletion until memberships are handled
Workspace → Projects	Restrict deletion while projects exist
User → Project creator	Preserve creator attribution
User → Audit event actor	Set NULL to preserve history
Workspace → Audit event	Set NULL if workspace is eventually removed


Additional integrity rules:
1. Every workspace must have at least one owner.
2. The last workspace owner cannot remove their own ownership.
3. Registration must create the user, applicable authentication record, personal workspace, and owner membership atomically.
4. Project archival must preserve the existing project record.
5. Audit history must remain available after account deactivation.
6. A single external provider identity can belong to only one CloudForge user.
7. A Google-only user must be valid without a user_credentials row.
8. Account linking must not rely on an unverified email match.
The last-owner rule and multi-record registration workflow require transactional application logic or a database-level mechanism.
6. Authentication Flows and Security
6.1 Email/password registration
1. Validate and normalize the submitted email address and validate the password policy.
2. Check case-insensitive email uniqueness.
3. Hash the password using Argon2id.
4. In one database transaction, create the users record, user_credentials record, personal workspaces record, and Owner workspace_memberships record.
5. Record a user.registered audit event without storing credentials or secrets.
6. Establish a CloudForge browser session only after successful registration and any required verification policy.
6.2 Email/password sign-in
1. Normalize the submitted email address.
2. Find the CloudForge user using the normalized/case-insensitive email.
3. Reject inactive accounts.
4. Verify the submitted password against the Argon2id hash.
5. Establish a new server-managed session and rotate the session identifier.
6. Record the authentication event without recording the password or session token.
6.3 Google sign-in
1. The browser starts the Google OpenID Connect authorization flow using the configured CloudForge OAuth client.
2. The Flask backend validates OAuth state and nonce and verifies the returned identity token, including signature, issuer, audience, and expiry.
3. Resolve the identity using (provider='google', provider_user_id=<verified sub>).
4. If the identity is already linked, authenticate the associated CloudForge user.
5. If it is new, apply the approved account-creation/account-linking policy. Require a verified email for any email-based account discovery; never link solely on an unverified email match.
6. For a new CloudForge user, create the user, Google identity, personal workspace, and Owner membership atomically.
7. Establish a CloudForge-managed browser session. Do not use the Google ID token as the CloudForge session token.
6.4 Browser session security
- Use Secure, HttpOnly, and appropriate SameSite cookie attributes in production.
- Protect state-changing cookie-authenticated requests with CSRF protection.
- Rotate session identifiers after authentication and privilege changes.
- Enforce session expiration and logout/revocation behavior.
- Configure CORS narrowly for trusted CloudForge frontend origins; do not use wildcard origins with credentialed requests.
- Keep OAuth client secrets and signing/session secrets in server-side environment variables or secret management, never in frontend source code.
- Use HTTPS for all production authentication callbacks and authenticated API traffic.
6.5 CLI authentication
The CLI must not depend on a browser session cookie. Use a dedicated short-lived access-token and refresh/device authorization strategy. Tokens must be scoped, revocable, stored securely on the client, and never written to logs. The exact token/session tables will be added when the CLI authentication flow is implemented.
7. Authorization Architecture
CloudForge uses workspace membership as the basis of project authorization.

A project ID alone must never grant access.

Before performing a project operation, the backend must verify:
1. The user is authenticated.
2. The requested project exists.
3. The project belongs to a particular workspace.
4. The user has a membership in that workspace.
5. The user's role permits the requested action.
This protects against insecure direct object reference attacks, including users attempting to access other users' projects by changing API identifiers.

Authentication establishes who the user is. Authorization determines what that user is allowed to do. A successful Google login must never bypass CloudForge's workspace membership and role checks.
8. Future Schema Extensions
The following entities are intentionally deferred until their respective features are implemented. The initial authentication tables (user_credentials and user_identities) are part of the initial schema and are not deferred.
Future Entity	Responsibility
deployments	Deployment history and orchestration
repositories	GitHub repository connections
environments	Development, staging and production
runner_jobs	Cloud Runner execution jobs
cloud_credentials	Cloud provider credential references
infrastructure_resources	Terraform resource tracking
authentication_sessions	If persistent server-side session tracking is required
refresh_tokens	If required for the CLI/device authorization strategy
external_provider_tokens	Only if future provider API access requires securely encrypted token storage


9. Approved Architecture Decisions
Decision	Approved Design
Database	Neon PostgreSQL
Primary keys	UUID
Workspace creation	Automatic personal workspace during registration
Workspace roles	Owner, Admin, Developer, Viewer
Project deletion	Archive instead of permanent deletion
Project ownership	Workspace-based
Membership model	Many-to-many
Authentication architecture	Hybrid: Google OpenID Connect + Flask-managed email/password
Password storage	Optional Argon2id credential in user_credentials
External identities	user_identities, keyed by provider and stable provider subject
Browser sessions	Flask-managed secure HttpOnly cookies with CSRF protection
CLI authentication	Separate short-lived token/device authorization strategy
Audit metadata	PostgreSQL JSONB
Schema migrations	Flask-Migrate / Alembic


10. Implementation Status
Current status: Approved design, implementation pending.
Implementation Task	Status
Schema architecture	Approved
Authentication-aware schema design	Approved
SQLAlchemy models	Pending
Database constraints	Pending
Database indexes	Pending
Initial migration	Pending
Neon migration execution	Pending
Seed/demo data	Pending
Database integration tests	Pending
Google OAuth configuration and backend flow	Pending
Flask email/password authentication	Pending
Browser session and CSRF implementation	Pending
CLI authentication strategy implementation	Pending


11. Future Interview Discussion Points
This architecture provides several useful topics for technical interviews:
1. Why PostgreSQL instead of a document database?
2. Why use UUID primary keys?
3. Why use a separate membership table?
4. How does workspace-level multi-user authorization work?
5. Why enforce constraints in both the application and database?
6. Why use JSONB for audit metadata?
7. How do transactions protect user registration?
8. How does CloudForge preserve project and audit history?
9. How can one CloudForge user support both local credentials and Google identity?
10. Why should an external identity be keyed by the provider's stable subject (sub) rather than email?
11. Why is authentication separate from authorization?
12. Why should the Google identity token not be used as the CloudForge application session?
Important: This document describes the approved architecture. Implementation details and actual database behavior should be updated after migrations and tests are completed.

Authentication boundary: Google is an external identity provider only. CloudForge remains responsible for its own user records, sessions, workspace membership, authorization, and audit history. Email/password authentication is implemented by the Flask backend using Argon2id. Both login methods resolve to the same users record.