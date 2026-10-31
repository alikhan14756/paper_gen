from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.core.database import Base, engine, SessionLocal
from app.core.security import hash_password, ROLE_SUPER_ADMIN, ROLE_SCHOOL_ADMIN, ROLE_TEACHER
from app.models.core_entities import School, User, SchoolMembership, SubscriptionPlan, SchoolSubscription
from app.models.paper_entities import ExamTemplate

def init_db():
    Base.metadata.create_all(bind=engine)

    # Seamlessly add any newly added enterprise columns if running on SQLite
    try:
        with engine.connect() as conn:
            if "sqlite" in str(engine.url):
                p_cols = [r[1] for r in conn.exec_driver_sql("PRAGMA table_info(papers)").fetchall()]
                if "verification_code" not in p_cols:
                    conn.exec_driver_sql("ALTER TABLE papers ADD COLUMN verification_code VARCHAR(64)")
                if "watermark_text" not in p_cols:
                    conn.exec_driver_sql("ALTER TABLE papers ADD COLUMN watermark_text VARCHAR(100)")

                q_cols = [r[1] for r in conn.exec_driver_sql("PRAGMA table_info(questions)").fetchall()]
                if "blooms_level" not in q_cols:
                    conn.exec_driver_sql("ALTER TABLE questions ADD COLUMN blooms_level VARCHAR(50) DEFAULT 'Understand'")
                if "source_page" not in q_cols:
                    conn.exec_driver_sql("ALTER TABLE questions ADD COLUMN source_page INTEGER")
                if "source_excerpt" not in q_cols:
                    conn.exec_driver_sql("ALTER TABLE questions ADD COLUMN source_excerpt TEXT")
                if "confidence_score" not in q_cols:
                    conn.exec_driver_sql("ALTER TABLE questions ADD COLUMN confidence_score FLOAT DEFAULT 0.95")
                if "quality_score" not in q_cols:
                    conn.exec_driver_sql("ALTER TABLE questions ADD COLUMN quality_score FLOAT DEFAULT 0.92")
                if "duplicate_risk" not in q_cols:
                    conn.exec_driver_sql("ALTER TABLE questions ADD COLUMN duplicate_risk FLOAT DEFAULT 0.03")

                u_cols = [r[1] for r in conn.exec_driver_sql("PRAGMA table_info(users)").fetchall()]
                if "is_email_verified" not in u_cols:
                    conn.exec_driver_sql("ALTER TABLE users ADD COLUMN is_email_verified BOOLEAN DEFAULT 1")
                if "verification_code" not in u_cols:
                    conn.exec_driver_sql("ALTER TABLE users ADD COLUMN verification_code VARCHAR(32)")
                if "verification_code_expires_at" not in u_cols:
                    conn.exec_driver_sql("ALTER TABLE users ADD COLUMN verification_code_expires_at DATETIME")

                s_cols = [r[1] for r in conn.exec_driver_sql("PRAGMA table_info(schools)").fetchall()]
                if "subscription_tier" not in s_cols:
                    conn.exec_driver_sql("ALTER TABLE schools ADD COLUMN subscription_tier VARCHAR(50) DEFAULT 'free_trial'")
                if "is_paid" not in s_cols:
                    conn.exec_driver_sql("ALTER TABLE schools ADD COLUMN is_paid BOOLEAN DEFAULT 0")
                if "free_papers_per_subject" not in s_cols:
                    conn.exec_driver_sql("ALTER TABLE schools ADD COLUMN free_papers_per_subject INTEGER DEFAULT 2")

                b_cols = [r[1] for r in conn.exec_driver_sql("PRAGMA table_info(books)").fetchall()]
                if "is_global" not in b_cols:
                    conn.exec_driver_sql("ALTER TABLE books ADD COLUMN is_global BOOLEAN DEFAULT 0")

                conn.commit()
    except Exception as e:
        pass
    
    db: Session = SessionLocal()
    try:
        # Check if already initialized
        existing_super = db.query(User).filter(User.role == ROLE_SUPER_ADMIN).first()
        if existing_super:
            return

        # 1. Seed Subscription Plans
        plan_standard = SubscriptionPlan(
            name="Standard School Plan",
            slug="standard",
            price_monthly=15000.0,
            price_yearly=150000.0,
            max_teachers=25,
            max_monthly_papers=200,
            max_file_size_mb=50,
            features_json='{"docx_export": true, "urdu_support": true, "ai_generation": true}',
            is_active=True
        )
        plan_premium = SubscriptionPlan(
            name="Premium Enterprise Plan",
            slug="premium",
            price_monthly=35000.0,
            price_yearly=350000.0,
            max_teachers=100,
            max_monthly_papers=1000,
            max_file_size_mb=100,
            features_json='{"docx_export": true, "urdu_support": true, "ai_generation": true, "priority_ocr": true}',
            is_active=True
        )
        db.add_all([plan_standard, plan_premium])
        db.commit()
        db.refresh(plan_standard)
        db.refresh(plan_premium)

        # 2. Seed Default Demo School
        school = School(
            name="Lahore Grammar School (LGS)",
            slug="lgs",
            logo_url="",
            address="Gulberg III, Lahore, Pakistan",
            contact_email="info@lgs.edu.pk",
            phone_number="+92 42 35712345",
            default_language="en",
            status="active",
            max_teachers=50,
            max_monthly_papers=500,
            papers_generated_this_month=0,
            is_active=True,
        )
        db.add(school)
        db.commit()
        db.refresh(school)

        # 3. Seed School Subscription
        sub = SchoolSubscription(
            school_id=school.id,
            plan_id=plan_premium.id,
            status="active",
            current_period_start=datetime.now(timezone.utc),
            current_period_end=datetime.now(timezone.utc) + timedelta(days=365),
        )
        db.add(sub)

        # 4. Seed Super Admin
        super_admin = User(
            email="superadmin@examforge.ai",
            hashed_password=hash_password("Admin@1234"),
            full_name="Platform Super Admin",
            role=ROLE_SUPER_ADMIN,
            is_active=True,
            is_email_verified=True,
            school_id=None,
        )
        db.add(super_admin)

        # 5. Seed School Admin
        school_admin = User(
            email="admin@lgs.edu.pk",
            hashed_password=hash_password("Admin@1234"),
            full_name="Principal Ahmad Raza",
            role=ROLE_SCHOOL_ADMIN,
            is_active=True,
            is_email_verified=True,
            school_id=school.id,
        )
        db.add(school_admin)
        db.commit()
        db.refresh(school_admin)

        # 6. Seed Teacher
        teacher = User(
            email="teacher@lgs.edu.pk",
            hashed_password=hash_password("Teacher@1234"),
            full_name="Prof. Fatima Malik",
            role=ROLE_TEACHER,
            is_active=True,
            is_email_verified=True,
            school_id=school.id,
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)

        # 7. Seed School Memberships
        mem_admin = SchoolMembership(
            school_id=school.id,
            user_id=school_admin.id,
            role=ROLE_SCHOOL_ADMIN,
            is_active=True
        )
        mem_teacher = SchoolMembership(
            school_id=school.id,
            user_id=teacher.id,
            role=ROLE_TEACHER,
            is_active=True
        )
        db.add_all([mem_admin, mem_teacher])

        # 8. Seed Default Exam Template
        template = ExamTemplate(
            school_id=school.id,
            created_by_id=school_admin.id,
            name="Standard Board Exam Template (50 Marks)",
            description="10 MCQs, 5 Short Questions (from 8), 2 Long Questions (from 3)",
            grade="10",
            subject="General",
            language="en",
            total_marks=50,
            time_allowed_minutes=120,
            sections_config_json='[{"title": "Section A", "type": "mcq", "total": 10, "attempt": 10, "marks": 1}, {"title": "Section B", "type": "short", "total": 8, "attempt": 5, "marks": 4}, {"title": "Section C", "type": "long", "total": 3, "attempt": 2, "marks": 10}]',
            is_school_default=True
        )
        db.add(template)

        db.commit()
        print("Database schema created and initial accounts, memberships, and subscription plans seeded successfully!")
    finally:
        db.close()
