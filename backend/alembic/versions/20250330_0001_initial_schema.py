"""initial schema

Revision ID: 0001
Revises:
Create Date: 2025-03-30

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("admin_approved", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("consent_data_processing_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_name"), "users", ["name"], unique=False)
    op.create_index(op.f("ix_users_role"), "users", ["role"], unique=False)

    op.create_table(
        "fakultet",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("naziv", sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_fakultet_id"), "fakultet", ["id"], unique=False)

    op.create_table(
        "studijski_program",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("fakultet_id", sa.Integer(), nullable=False),
        sa.Column("tip_studija", sa.String(length=40), nullable=False),
        sa.Column("godina", sa.Integer(), nullable=False),
        sa.Column("datum_pocetka", sa.Date(), nullable=False),
        sa.Column("datum_kraja", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(["fakultet_id"], ["fakultet.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_studijski_program_fakultet_id"), "studijski_program", ["fakultet_id"], unique=False)
    op.create_index(op.f("ix_studijski_program_id"), "studijski_program", ["id"], unique=False)

    op.create_table(
        "tehnologija",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("naziv", sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("naziv"),
    )
    op.create_index(op.f("ix_tehnologija_id"), "tehnologija", ["id"], unique=False)

    op.create_table(
        "student",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("ime", sa.String(length=100), nullable=False),
        sa.Column("prezime", sa.String(length=100), nullable=False),
        sa.Column("kontakt_telefon", sa.String(length=512), nullable=True),
        sa.Column("datum_rodjenja", sa.String(length=512), nullable=True),
        sa.Column("adresa", sa.String(length=1024), nullable=True),
        sa.Column("prosek", sa.Float(), nullable=True),
        sa.Column("studijski_program_id", sa.Integer(), nullable=False),
        sa.Column("cv_file_path", sa.String(length=500), nullable=True),
        sa.Column("cv_original_filename", sa.String(length=255), nullable=True),
        sa.Column("last_edit_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deletion_requested_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["studijski_program_id"], ["studijski_program.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_student_id"), "student", ["id"], unique=False)
    op.create_index(op.f("ix_student_studijski_program_id"), "student", ["studijski_program_id"], unique=False)
    op.create_index(op.f("ix_student_user_id"), "student", ["user_id"], unique=True)

    op.create_table(
        "projekti",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("datum_pocetka_izrade", sa.Date(), nullable=False),
        sa.Column("datum_kraja_izrade_projekta", sa.Date(), nullable=True),
        sa.Column("opis", sa.String(length=1000), nullable=False),
        sa.Column("id_studenta", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["id_studenta"], ["student.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_projekti_id"), "projekti", ["id"], unique=False)
    op.create_index(op.f("ix_projekti_id_studenta"), "projekti", ["id_studenta"], unique=False)

    op.create_table(
        "student_tehnologija",
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("tehnologija_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["student.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tehnologija_id"], ["tehnologija.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("student_id", "tehnologija_id"),
    )

    op.create_table(
        "company_profile",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("company_name", sa.String(length=300), nullable=False),
        sa.Column("contact_person", sa.String(length=200), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_company_profile_id"), "company_profile", ["id"], unique=False)
    op.create_index(op.f("ix_company_profile_user_id"), "company_profile", ["user_id"], unique=True)

    op.create_table(
        "access_grant",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("company_profile_id", sa.Integer(), nullable=False),
        sa.Column("max_cv_count", sa.Integer(), nullable=False),
        sa.Column("valid_from", sa.Date(), nullable=False),
        sa.Column("valid_until", sa.Date(), nullable=False),
        sa.Column("used_cv_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("granted_by_user_id", sa.Integer(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["company_profile_id"], ["company_profile.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["granted_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_access_grant_company_profile_id"), "access_grant", ["company_profile_id"], unique=False)
    op.create_index(op.f("ix_access_grant_id"), "access_grant", ["id"], unique=False)

    op.create_table(
        "company_student_access",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("access_grant_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("granted_by_user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["access_grant_id"], ["access_grant.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["granted_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["student_id"], ["student.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("access_grant_id", "student_id", name="uq_grant_student"),
    )
    op.create_index(op.f("ix_company_student_access_access_grant_id"), "company_student_access", ["access_grant_id"], unique=False)
    op.create_index(op.f("ix_company_student_access_id"), "company_student_access", ["id"], unique=False)
    op.create_index(op.f("ix_company_student_access_student_id"), "company_student_access", ["student_id"], unique=False)

    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=True),
        sa.Column("resource_id", sa.Integer(), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("request_id", sa.String(length=64), nullable=True),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_log_action"), "audit_log", ["action"], unique=False)
    op.create_index(op.f("ix_audit_log_created_at"), "audit_log", ["created_at"], unique=False)
    op.create_index(op.f("ix_audit_log_id"), "audit_log", ["id"], unique=False)
    op.create_index(op.f("ix_audit_log_request_id"), "audit_log", ["request_id"], unique=False)
    op.create_index(op.f("ix_audit_log_resource_type"), "audit_log", ["resource_type"], unique=False)
    op.create_index(op.f("ix_audit_log_user_id"), "audit_log", ["user_id"], unique=False)

    op.create_table(
        "refresh_token",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(op.f("ix_refresh_token_id"), "refresh_token", ["id"], unique=False)
    op.create_index(op.f("ix_refresh_token_token_hash"), "refresh_token", ["token_hash"], unique=True)
    op.create_index(op.f("ix_refresh_token_user_id"), "refresh_token", ["user_id"], unique=False)

    op.create_table(
        "edit_grant",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("granted_by_user_id", sa.Integer(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("consumed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["granted_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["student_id"], ["student.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_edit_grant_id"), "edit_grant", ["id"], unique=False)
    op.create_index(op.f("ix_edit_grant_student_id"), "edit_grant", ["student_id"], unique=False)

    op.create_table(
        "deletion_request",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("requested_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processed_by_user_id", sa.Integer(), nullable=True),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(["processed_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_deletion_request_id"), "deletion_request", ["id"], unique=False)
    op.create_index(op.f("ix_deletion_request_status"), "deletion_request", ["status"], unique=False)
    op.create_index(op.f("ix_deletion_request_user_id"), "deletion_request", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_table("deletion_request")
    op.drop_table("edit_grant")
    op.drop_table("refresh_token")
    op.drop_table("audit_log")
    op.drop_table("company_student_access")
    op.drop_table("access_grant")
    op.drop_table("company_profile")
    op.drop_table("student_tehnologija")
    op.drop_table("projekti")
    op.drop_table("student")
    op.drop_table("tehnologija")
    op.drop_table("studijski_program")
    op.drop_table("fakultet")
    op.drop_table("users")
