from app.extensions import db
from app.models import (
    Project,
    User,
    UserCredential,
    UserIdentity,
    Workspace,
    WorkspaceMembership,
)


def test_complete_user_workspace_project_relationships(app):
    with app.app_context():
        # 1. Create a user
        user = User(
            email="ankit@example.com",
            full_name="Test User",
        )

        # 2. Attach email/password credentials
        credential = UserCredential(
            password_hash="test-password-hash",
        )
        user.credential = credential

        # 3. Attach a Google identity
        identity = UserIdentity(
            provider="google",
            provider_user_id="google-test-user-123",
            provider_email="ankit@example.com",
        )
        user.identities.append(identity)

        # 4. Create a personal workspace
        workspace = Workspace(
            name="Personal Workspace",
            slug="personal-workspace",
            kind="personal",
            creator=user,
        )

        # 5. Add the user as workspace owner
        membership = WorkspaceMembership(
            user=user,
            workspace=workspace,
            role="owner",
        )

        # 6. Create a project
        project = Project(
            name="CloudForge Test Project",
            slug="cloudforge-test-project",
            status="active",
            workspace=workspace,
            creator=user,
        )

        db.session.add(user)
        db.session.add(workspace)
        db.session.add(membership)
        db.session.add(project)
        db.session.commit()

        # Verify persisted relationships
        assert user.credential is not None
        assert user.credential.password_hash == "test-password-hash"

        assert len(user.identities) == 1
        assert user.identities[0].provider == "google"

        assert workspace.creator.id == user.id
        assert membership.user.id == user.id
        assert membership.workspace.id == workspace.id
        assert membership.role == "owner"

        assert project.workspace.id == workspace.id
        assert project.creator.id == user.id

        assert project in workspace.projects
        assert workspace in user.created_workspaces
        assert project in user.created_projects