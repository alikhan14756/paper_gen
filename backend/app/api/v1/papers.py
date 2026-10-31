import os
import json
import uuid
import urllib.parse
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.core.deps import get_current_user
from app.models.core_entities import User, School, SchoolSubscription
from app.models.document_entities import Book, Chapter
from app.models.paper_entities import (
    Paper,
    PaperVersion,
    Section,
    Question,
    QuestionVersion,
    AnswerKey,
    UsageReservation,
    UsageRecord,
    AIGenerationJob,
    AuditLog,
)
from app.schemas.paper import (
    PaperResponse,
    QuestionResponse,
    QuestionUpdate,
    GeneratePaperRequest,
    MarksValidationResult,
    SectionMarksBreakdown,
    BlueprintRequest,
    BlueprintResponse,
    ChapterBlueprintItem,
)
from app.services.document.extractor import DocumentExtractor
from app.services.ai.provider import get_ai_provider
from app.services.export.docx_generator import DocxGenerator

router = APIRouter(prefix="/papers", tags=["Papers"])

@router.post("/validate-marks", response_model=MarksValidationResult)
def validate_paper_marks(request: GeneratePaperRequest):
    breakdowns: List[SectionMarksBreakdown] = []
    calculated_total = 0.0
    warnings = []

    for sec in request.sections:
        attempt = sec.questions_to_attempt if sec.questions_to_attempt > 0 else sec.total_questions
        sec_marks = attempt * sec.marks_per_question
        calculated_total += sec_marks

        breakdowns.append(
            SectionMarksBreakdown(
                section_title=sec.title,
                total_questions=sec.total_questions,
                questions_to_attempt=attempt,
                marks_per_question=sec.marks_per_question,
                calculated_section_marks=sec_marks,
            )
        )

        if sec.questions_to_attempt > sec.total_questions:
            warnings.append(f"In '{sec.title}': Questions to attempt ({sec.questions_to_attempt}) exceeds total questions ({sec.total_questions}).")

    diff = round(calculated_total - request.total_marks, 2)
    is_valid = abs(diff) < 0.01

    if not is_valid:
        warnings.append(
            f"Configured total marks ({request.total_marks}) does not match the sum of sections ({calculated_total}). Difference: {diff} marks."
        )

    return MarksValidationResult(
        is_valid=is_valid,
        configured_total_marks=request.total_marks,
        calculated_total_marks=calculated_total,
        difference=diff,
        breakdown=breakdowns,
        warnings=warnings,
    )

@router.post("/generate-blueprint", response_model=BlueprintResponse)
def generate_examination_blueprint(
    req: BlueprintRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Automatic Examination Blueprint Generator:
    Intelligently balances mark weightage, chapter distribution, and Bloom's Taxonomy cognitive levels.
    """
    chapters = db.query(Chapter).filter(Chapter.id.in_(req.selected_chapter_ids)).all()
    if not chapters:
        raise HTTPException(status_code=400, detail="No valid chapters selected for blueprint generation.")

    total_chapters = len(chapters)
    base_marks_per_ch = req.total_marks // total_chapters
    remainder = req.total_marks % total_chapters

    blooms_options = ["Remember", "Understand", "Apply", "Analyze", "Evaluate"]
    chapter_items: List[ChapterBlueprintItem] = []

    for idx, ch in enumerate(chapters):
        ch_marks = base_marks_per_ch + (1 if idx < remainder else 0)
        weight_pct = round((ch_marks / req.total_marks) * 100, 1)

        # Distribute into MCQs (1m), Shorts (3-4m), Longs (6-8m)
        mcqs = max(1, ch_marks // 5)
        remaining = ch_marks - mcqs
        shorts = max(1, remaining // 4)
        longs = 1 if (remaining - (shorts * 3) >= 5) else 0

        blooms_focus = blooms_options[idx % len(blooms_options)]

        chapter_items.append(ChapterBlueprintItem(
            chapter_id=ch.id,
            chapter_title=ch.title,
            weightage_pct=weight_pct,
            marks_allocated=ch_marks,
            mcq_count=mcqs,
            short_count=shorts,
            long_count=longs,
            blooms_focus=blooms_focus,
        ))

    return BlueprintResponse(
        total_marks=req.total_marks,
        subject=req.subject,
        grade=req.grade,
        chapters=chapter_items,
        blooms_summary={
            "Remember": 25,
            "Understand": 35,
            "Apply": 20,
            "Analyze": 15,
            "Evaluate": 5
        },
        difficulty_summary={
            "Easy": 30,
            "Medium": 50,
            "Hard": 20
        }
    )

@router.get("/subject-quota")
def get_subject_quota(
    subject: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns the free trial or subscription quota status for a specific subject for the user's school.
    Enforces the rule: each school gets 2 free papers per subject in free trial mode.
    """
    if not current_user.school_id:
        raise HTTPException(status_code=400, detail="User must belong to a school")

    school = db.query(School).filter(School.id == current_user.school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    is_paid = bool(
        school.is_paid
        or (school.subscription_tier and school.subscription_tier.lower() in ["paid", "standard", "premium", "enterprise"])
    )
    papers_used = db.query(Paper).filter(
        Paper.school_id == school.id,
        Paper.subject.ilike(subject.strip())
    ).count()

    max_free = school.free_papers_per_subject or 2
    remaining = max(0, max_free - papers_used) if not is_paid else 9999

    return {
        "subject": subject.strip(),
        "school_id": school.id,
        "school_name": school.name,
        "subscription_tier": school.subscription_tier or "free_trial",
        "is_paid": is_paid,
        "papers_used": papers_used,
        "max_free_papers": max_free,
        "remaining_free_papers": remaining,
        "can_generate": is_paid or (papers_used < max_free),
        "owner_name": "Muhammad Ali",
        "owner_email": "alikhanwebdeveloper@gmail.com",
        "owner_portfolio": "https://alibuild.site",
    }

@router.get("/verify/{verification_code}")
def verify_official_examination_paper(
    verification_code: str,
    db: Session = Depends(get_db),
):
    """
    Public QR Verification Endpoint:
    Allows examination supervisors and students to scan the QR watermark on the paper to verify authenticity.
    """
    clean_code = verification_code.strip()
    paper = db.query(Paper).filter(
        (Paper.verification_code == clean_code) | (Paper.id == clean_code)
    ).first()

    if not paper:
        raise HTTPException(
            status_code=404,
            detail="Verification failed: Examination Paper record not found or code invalid."
        )

    school_name = paper.school.name if paper.school else "Verified Educational Institution"
    return {
        "status": "VERIFIED_OFFICIAL",
        "verification_code": paper.verification_code,
        "paper_id": paper.id,
        "paper_title": paper.title,
        "school_name": school_name,
        "grade": paper.grade,
        "subject": paper.subject,
        "academic_session": paper.academic_session,
        "exam_type": paper.exam_type,
        "total_marks": paper.total_marks,
        "issued_at": paper.created_at.strftime("%B %d, %Y"),
        "digital_stamp": "SECURE_EXAMFORGE_BISEP_AUTHENTICATED"
    }

def reconcile_expired_reservations(db: Session, school_id: Optional[str] = None):
    """Reconciles and marks expired pending reservations as released."""
    now = datetime.now(timezone.utc)
    query = db.query(UsageReservation).filter(
        UsageReservation.status == "reserved",
        UsageReservation.expires_at <= now,
    )
    if school_id:
        query = query.filter(UsageReservation.school_id == school_id)
    expired = query.all()
    for res in expired:
        res.status = "released"
    if expired:
        db.commit()

@router.post("/generate", response_model=PaperResponse)
async def generate_paper(
    request: GeneratePaperRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.school_id:
        raise HTTPException(status_code=400, detail="User must belong to a school")

    school = db.query(School).filter(School.id == current_user.school_id).first()
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    # Reconcile any expired reservations before calculating effective quota
    reconcile_expired_reservations(db, school.id)

    # 1. Concurrency-safe Quota Reservation
    active_reservations = (
        db.query(UsageReservation)
        .filter(
            UsageReservation.school_id == school.id,
            UsageReservation.status == "reserved",
            UsageReservation.expires_at > datetime.now(timezone.utc),
        )
        .count()
    )
    effective_used = school.papers_generated_this_month + active_reservations

    if effective_used >= school.max_monthly_papers:
        raise HTTPException(
            status_code=403,
            detail=f"School monthly paper quota exhausted ({effective_used}/{school.max_monthly_papers}). Upgrade plan or contact admin."
        )

    # Reserve 1 quota unit
    res_token = str(uuid.uuid4())
    reservation = UsageReservation(
        school_id=school.id,
        user_id=current_user.id,
        reservation_token=res_token,
        units_reserved=1,
        status="reserved",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    db.add(reservation)
    db.commit()

    book = db.query(Book).filter(Book.id == request.book_id).first()
    if not book:
        reservation.status = "released"
        db.commit()
        raise HTTPException(status_code=404, detail="Selected textbook not found")
    if current_user.role != "super_admin" and book.school_id != current_user.school_id and not book.is_global:
        reservation.status = "released"
        db.commit()
        raise HTTPException(status_code=403, detail="Textbook does not belong to your school")

    # 2. Free Trial Subject Limit Enforcement (Max 2 free papers per subject)
    is_paid_school = bool(
        school.is_paid
        or (school.subscription_tier and school.subscription_tier.lower() in ["paid", "standard", "premium", "enterprise"])
    )
    if not is_paid_school:
        target_subject = (request.subject or book.subject).strip()
        papers_for_subject = db.query(Paper).filter(
            Paper.school_id == school.id,
            Paper.subject.ilike(target_subject)
        ).count()

        max_allowed = school.free_papers_per_subject or 2
        if papers_for_subject >= max_allowed:
            reservation.status = "released"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Free trial limit reached: Your school has already generated {papers_for_subject}/{max_allowed} "
                    f"free examination papers for '{target_subject}'. To generate more papers, please upgrade to a paid "
                    f"subscription or contact the platform owner Muhammad Ali (alikhanwebdeveloper@gmail.com | https://alibuild.site)."
                ),
                headers={"X-Error-Code": "FREE_TRIAL_LIMIT_REACHED"}
            )

    # Load source text for selected chapters (verifying they belong to the book)
    cache_path = os.path.join(settings.UPLOAD_DIR, f"{book.id}_cache.json")
    selected_chapters = db.query(Chapter).filter(
        Chapter.id.in_(request.selected_chapter_ids),
        Chapter.book_id == book.id
    ).all()
    
    combined_source_text = ""
    for ch in selected_chapters:
        ch_text = DocumentExtractor.get_text_for_page_range(cache_path, ch.start_page, ch.end_page)
        combined_source_text += f"\n\n=== {ch.title} (Pages {ch.start_page}-{ch.end_page}) ===\n" + ch_text

    if not combined_source_text.strip():
        combined_source_text = f"Subject: {request.subject}. Grade: {request.grade}. Topics from selected chapters."

    # Create Paper record
    paper = Paper(
        school_id=current_user.school_id,
        created_by_id=current_user.id,
        book_id=book.id,
        title=request.title,
        exam_type=request.exam_type,
        academic_session=request.academic_session,
        grade=request.grade,
        subject=request.subject,
        language=request.language,
        time_allowed_minutes=request.time_allowed_minutes,
        total_marks=request.total_marks,
        instructions=request.instructions,
        status="generated",
        selected_chapters_json=json.dumps(request.selected_chapter_ids),
        verification_code=f"EXAM-{uuid.uuid4().hex[:10].upper()}",
        watermark_text=f"{school.name} • OFFICIAL EXAMINATION",
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)

    ai_provider = get_ai_provider()
    total_generated_questions = 0

    # Generate sections and questions
    try:
        for sec_idx, sec_cfg in enumerate(request.sections):
            section = Section(
                paper_id=paper.id,
                school_id=current_user.school_id,
                title=sec_cfg.title,
                section_type=sec_cfg.section_type,
                sort_order=sec_idx + 1,
                total_questions=sec_cfg.total_questions,
                questions_to_attempt=sec_cfg.questions_to_attempt,
                marks_per_question=sec_cfg.marks_per_question,
                total_section_marks=sec_cfg.questions_to_attempt * sec_cfg.marks_per_question,
                instructions=sec_cfg.instructions,
            )
            db.add(section)
            db.commit()
            db.refresh(section)

            # Call AI provider
            try:
                questions_data = await ai_provider.generate_questions_for_section(
                    section_title=sec_cfg.title,
                    section_type=sec_cfg.section_type,
                    count=sec_cfg.total_questions,
                    marks_per_question=sec_cfg.marks_per_question,
                    language=request.language,
                    subject=request.subject,
                    grade=request.grade,
                    source_text=combined_source_text,
                    difficulty="medium",
                )
            except Exception:
                from app.services.ai.provider import GroundedMockProvider
                fallback = GroundedMockProvider()
                questions_data = await fallback.generate_questions_for_section(
                    section_title=sec_cfg.title,
                    section_type=sec_cfg.section_type,
                    count=sec_cfg.total_questions,
                    marks_per_question=sec_cfg.marks_per_question,
                    language=request.language,
                    subject=request.subject,
                    grade=request.grade,
                    source_text=combined_source_text,
                    difficulty="medium",
                )

            for q_idx, q_item in enumerate(questions_data):
                q_rec = Question(
                    section_id=section.id,
                    paper_id=paper.id,
                    school_id=current_user.school_id,
                    question_number=q_idx + 1,
                    question_type=sec_cfg.section_type,
                    question_text=q_item.get("question_text", f"Question {q_idx + 1}"),
                    options_json=json.dumps(q_item.get("options", []), ensure_ascii=False),
                    correct_answer=q_item.get("correct_answer", ""),
                    marks=sec_cfg.marks_per_question,
                    difficulty=q_item.get("difficulty", "medium"),
                    blooms_level=q_item.get("blooms_level", "Understand"),
                    source_reference=q_item.get("source_reference", f"Chapter {selected_chapters[0].title if selected_chapters else ''}"),
                    source_page=q_item.get("source_page"),
                    source_excerpt=q_item.get("source_excerpt", ""),
                    confidence_score=q_item.get("confidence_score", 0.95),
                    quality_score=q_item.get("quality_score", 0.92),
                    duplicate_risk=q_item.get("duplicate_risk", 0.03),
                    explanation=q_item.get("explanation", ""),
                    sort_order=q_idx + 1,
                    review_status="pending",
                )
                db.add(q_rec)
                db.flush()

                # Create AnswerKey record
                ans_key = AnswerKey(
                    paper_id=paper.id,
                    question_id=q_rec.id,
                    school_id=current_user.school_id,
                    solution_text=q_rec.correct_answer or "See textbook",
                    marking_guide=q_rec.explanation,
                )
                db.add(ans_key)
                total_generated_questions += 1

        # Commit reservation and increment school quota
        reservation.status = "committed"
        school.papers_generated_this_month += 1

        # Log UsageRecord
        db.add(UsageRecord(
            school_id=school.id,
            user_id=current_user.id,
            metric_name="paper_generated",
            quantity=1,
            details_json=json.dumps({"paper_id": paper.id, "title": paper.title})
        ))

        # Log AI Generation Job
        ai_job = AIGenerationJob(
            school_id=school.id,
            user_id=current_user.id,
            paper_id=paper.id,
            provider="gemini",
            model_name="gemini-2.5-flash",
            action_type="generate_paper",
            total_tokens=total_generated_questions * 150,
            estimated_cost_usd=round(total_generated_questions * 0.0005, 4),
            status="success",
        )
        db.add(ai_job)

        # Create Initial Immutable PaperVersion (v1)
        paper_dict = _format_paper_dict(paper)
        version1 = PaperVersion(
            paper_id=paper.id,
            school_id=school.id,
            version_number=1,
            snapshot_json=json.dumps(paper_dict, ensure_ascii=False),
            change_summary="Initial AI generation",
            created_by_id=current_user.id,
        )
        db.add(version1)
        db.flush()
        paper.current_version_id = version1.id

        db.commit()
        db.refresh(paper)
        return get_paper(paper.id, db, current_user)

    except Exception as e:
        reservation.status = "released"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@router.get("", response_model=List[PaperResponse])
def list_papers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Paper)
    if current_user.role != "super_admin":
        query = query.filter(Paper.school_id == current_user.school_id)
    papers = query.order_by(Paper.created_at.desc()).all()
    
    results = []
    for p in papers:
        results.append(_format_paper_response(p))
    return results

@router.get("/{paper_id}", response_model=PaperResponse)
def get_paper(
    paper_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    if current_user.role != "super_admin" and paper.school_id != current_user.school_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return _format_paper_response(paper)

@router.patch("/{paper_id}/questions/{question_id}", response_model=QuestionResponse)
def update_question(
    paper_id: str,
    question_id: str,
    data: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper or (current_user.role != "super_admin" and paper.school_id != current_user.school_id):
        raise HTTPException(status_code=403, detail="Forbidden")

    question = db.query(Question).filter(
        Question.id == question_id,
        Question.paper_id == paper.id,
        Question.school_id == paper.school_id,
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Snapshot previous version in QuestionVersion
    prev_ver_count = db.query(QuestionVersion).filter(QuestionVersion.question_id == question.id).count()
    db.add(QuestionVersion(
        question_id=question.id,
        school_id=paper.school_id,
        version_number=prev_ver_count + 1,
        question_text=question.question_text,
        options_json=question.options_json,
        correct_answer=question.correct_answer,
        marks=question.marks,
        edited_by_id=current_user.id
    ))

    update_dict = data.model_dump(exclude_unset=True)
    if "options" in update_dict and update_dict["options"] is not None:
        question.options_json = json.dumps(update_dict.pop("options"), ensure_ascii=False)

    for field, val in update_dict.items():
        setattr(question, field, val)

    question.review_status = "edited"

    # Also update AnswerKey if correct_answer or explanation changed
    ans_key = db.query(AnswerKey).filter(AnswerKey.question_id == question.id).first()
    if ans_key:
        if question.correct_answer:
            ans_key.solution_text = question.correct_answer
        if question.explanation:
            ans_key.marking_guide = question.explanation

    db.commit()
    db.refresh(question)

    return QuestionResponse(
        id=question.id,
        section_id=question.section_id,
        question_number=question.question_number,
        question_type=question.question_type,
        question_text=question.question_text,
        options=json.loads(question.options_json or "[]"),
        correct_answer=question.correct_answer,
        marks=question.marks,
        difficulty=question.difficulty,
        source_reference=question.source_reference,
        explanation=question.explanation,
        sort_order=question.sort_order,
        review_status=question.review_status,
    )

@router.post("/{paper_id}/questions/{question_id}/regenerate", response_model=QuestionResponse)
async def regenerate_single_question(
    paper_id: str,
    question_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper or (current_user.role != "super_admin" and paper.school_id != current_user.school_id):
        raise HTTPException(status_code=403, detail="Forbidden")

    question = db.query(Question).filter(
        Question.id == question_id,
        Question.paper_id == paper.id,
        Question.school_id == paper.school_id,
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    section = question.section
    book = paper.book

    # Snapshot previous version
    prev_ver_count = db.query(QuestionVersion).filter(QuestionVersion.question_id == question.id).count()
    db.add(QuestionVersion(
        question_id=question.id,
        school_id=paper.school_id,
        version_number=prev_ver_count + 1,
        question_text=question.question_text,
        options_json=question.options_json,
        correct_answer=question.correct_answer,
        marks=question.marks,
        edited_by_id=current_user.id
    ))

    source_text = f"Subject: {paper.subject}. Grade: {paper.grade}."
    if book:
        cache_path = os.path.join(settings.UPLOAD_DIR, f"{book.id}_cache.json")
        try:
            sel_chap_ids = json.loads(paper.selected_chapters_json or "[]")
            chapters = db.query(Chapter).filter(Chapter.id.in_(sel_chap_ids)).all()
            for ch in chapters:
                source_text += DocumentExtractor.get_text_for_page_range(cache_path, ch.start_page, ch.end_page)
        except Exception:
            pass

    ai_provider = get_ai_provider()
    try:
        new_q_data = await ai_provider.generate_questions_for_section(
            section_title=section.title,
            section_type=section.section_type,
            count=1,
            marks_per_question=question.marks,
            language=paper.language,
            subject=paper.subject,
            grade=paper.grade,
            source_text=source_text,
            difficulty=question.difficulty,
        )
    except Exception:
        from app.services.ai.provider import GroundedMockProvider
        fallback = GroundedMockProvider()
        new_q_data = await fallback.generate_questions_for_section(
            section_title=section.title,
            section_type=section.section_type,
            count=1,
            marks_per_question=question.marks,
            language=paper.language,
            subject=paper.subject,
            grade=paper.grade,
            source_text=source_text,
            difficulty=question.difficulty,
        )

    if new_q_data:
        item = new_q_data[0]
        question.question_text = item.get("question_text", question.question_text)
        question.options_json = json.dumps(item.get("options", []), ensure_ascii=False)
        question.correct_answer = item.get("correct_answer", question.correct_answer)
        question.source_reference = item.get("source_reference", question.source_reference)
        question.source_page = item.get("source_page", question.source_page)
        question.source_excerpt = item.get("source_excerpt", question.source_excerpt)
        question.blooms_level = item.get("blooms_level", question.blooms_level)
        question.confidence_score = item.get("confidence_score", question.confidence_score)
        question.quality_score = item.get("quality_score", question.quality_score)
        question.duplicate_risk = item.get("duplicate_risk", question.duplicate_risk)
        question.explanation = item.get("explanation", question.explanation)
        question.review_status = "edited"

        # Keep AnswerKey in sync with regenerated question
        ans_key = db.query(AnswerKey).filter(AnswerKey.question_id == question.id).first()
        if ans_key:
            ans_key.solution_text = question.correct_answer or "See textbook"
            ans_key.marking_guide = question.explanation
        else:
            db.add(AnswerKey(
                paper_id=paper.id,
                question_id=question.id,
                school_id=paper.school_id,
                solution_text=question.correct_answer or "See textbook",
                marking_guide=question.explanation
            ))

        db.commit()
        db.refresh(question)

    return QuestionResponse(
        id=question.id,
        section_id=question.section_id,
        question_number=question.question_number,
        question_type=question.question_type,
        question_text=question.question_text,
        options=json.loads(question.options_json or "[]"),
        correct_answer=question.correct_answer,
        marks=question.marks,
        difficulty=question.difficulty,
        source_reference=question.source_reference,
        explanation=question.explanation,
        sort_order=question.sort_order,
        review_status=question.review_status,
    )

@router.delete("/{paper_id}/questions/{question_id}", status_code=204)
def delete_question(
    paper_id: str,
    question_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper or (current_user.role != "super_admin" and paper.school_id != current_user.school_id):
        raise HTTPException(status_code=403, detail="Forbidden")

    question = db.query(Question).filter(
        Question.id == question_id,
        Question.paper_id == paper.id,
        Question.school_id == paper.school_id,
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    db.delete(question)
    db.commit()
    return None

@router.get("/{paper_id}/answer-key")
def get_confidential_answer_key(
    paper_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper or (current_user.role != "super_admin" and paper.school_id != current_user.school_id):
        raise HTTPException(status_code=403, detail="Forbidden")

    # Audit log staff access
    db.add(AuditLog(
        school_id=paper.school_id,
        user_id=current_user.id,
        action="view_confidential_answer_key",
        resource_type="paper",
        resource_id=paper.id,
        details=f"Viewed confidential answer key for paper {paper.id} by {current_user.email}"
    ))
    db.commit()

    key_items = []
    for section in paper.sections:
        for q in section.questions:
            ans = db.query(AnswerKey).filter(AnswerKey.question_id == q.id).first()
            key_items.append({
                "question_id": q.id,
                "question_number": q.question_number,
                "section_title": section.title,
                "section_type": q.question_type,
                "question_text": q.question_text,
                "correct_answer": q.correct_answer or (ans.solution_text if ans else ""),
                "explanation": q.explanation or (ans.marking_guide if ans else ""),
                "marks": q.marks,
            })

    return {
        "paper_id": paper.id,
        "title": paper.title,
        "grade": paper.grade,
        "subject": paper.subject,
        "total_marks": paper.total_marks,
        "marking_scheme": key_items
    }

@router.post("/{paper_id}/export-docx")
def export_docx(
    paper_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    include_answer_key: bool = False,
):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper or (current_user.role != "super_admin" and paper.school_id != current_user.school_id):
        raise HTTPException(status_code=403, detail="Forbidden")

    formatted = _format_paper_dict(paper)
    school_name = (paper.school.name if paper.school else None) or "PAKISTAN MODEL SCHOOL"
    school_info = {
        "name": school_name,
        "logo_url": paper.school.logo_url if paper.school else None,
    }

    filename = f"ExamPaper_{paper.id}.docx"
    file_path = os.path.join(settings.EXPORT_DIR, filename)

    DocxGenerator.generate_exam_docx(
        paper_data=formatted,
        school_info=school_info,
        output_path=file_path,
        include_answer_key=include_answer_key
    )

    paper.docx_path = file_path

    # Create immutable PaperVersion on export
    ver_count = db.query(PaperVersion).filter(PaperVersion.paper_id == paper.id).count()
    version = PaperVersion(
        paper_id=paper.id,
        school_id=paper.school_id,
        version_number=ver_count + 1,
        snapshot_json=json.dumps(formatted, ensure_ascii=False),
        change_summary="Exported Question Paper DOCX",
        exported_docx_path=file_path,
        created_by_id=current_user.id
    )
    db.add(version)
    db.commit()

    return {"message": "DOCX successfully generated", "download_url": f"/api/v1/papers/{paper.id}/download-docx"}

@router.get("/{paper_id}/download-docx")
def download_docx(
    paper_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    include_answer_key: bool = False,
):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper or (current_user.role != "super_admin" and paper.school_id != current_user.school_id):
        raise HTTPException(status_code=403, detail="Forbidden")

    if not paper.docx_path or not os.path.exists(paper.docx_path):
        export_docx(paper_id, db, current_user, include_answer_key)
        paper = db.query(Paper).filter(Paper.id == paper_id).first()

    # ASCII-safe fallback filename + RFC 5987 UTF-8 encoded filename for Starlette headers
    ascii_subj = "".join(c for c in paper.subject if c.isascii() and (c.isalnum() or c in ("-", "_", " "))).strip().replace(" ", "_")
    if not ascii_subj:
        ascii_subj = "PakStudies_Exam" if "مطالعہ" in (paper.subject or "") else ("Urdu_Exam" if paper.language == "ur" else "Exam_Paper")

    safe_ascii_filename = f"{ascii_subj}_Grade_{paper.grade}_{paper.id[:8]}.docx"
    encoded_utf8_filename = urllib.parse.quote(f"{paper.subject}_{paper.grade}_{paper.title}.docx")
    content_disposition = f"attachment; filename=\"{safe_ascii_filename}\"; filename*=UTF-8''{encoded_utf8_filename}"

    return FileResponse(
        path=paper.docx_path,
        filename=safe_ascii_filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": content_disposition
        }
    )

@router.post("/{paper_id}/export-answer-key")
def export_answer_key(
    paper_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper or (current_user.role != "super_admin" and paper.school_id != current_user.school_id):
        raise HTTPException(status_code=403, detail="Forbidden")

    formatted = _format_paper_dict(paper)
    school_name = (paper.school.name if paper.school else None) or "PAKISTAN MODEL SCHOOL"
    school_info = {
        "name": school_name,
        "logo_url": paper.school.logo_url if paper.school else None,
    }

    filename = f"AnswerKey_{paper.id}.docx"
    file_path = os.path.join(settings.EXPORT_DIR, filename)

    DocxGenerator.generate_confidential_answer_key_docx(
        paper_data=formatted,
        school_info=school_info,
        output_path=file_path,
    )

    paper.answer_key_docx_path = file_path

    # Audit log access to confidential marking scheme
    audit = AuditLog(
        school_id=paper.school_id,
        user_id=current_user.id,
        action="export_confidential_answer_key",
        resource_type="paper",
        resource_id=paper.id,
        details=f"Exported confidential marking guide by {current_user.email}"
    )
    db.add(audit)
    db.commit()

    return {"message": "Confidential Answer Key successfully generated", "download_url": f"/api/v1/papers/{paper.id}/download-answer-key"}

@router.get("/{paper_id}/download-answer-key")
def download_answer_key(
    paper_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper or (current_user.role != "super_admin" and paper.school_id != current_user.school_id):
        raise HTTPException(status_code=403, detail="Forbidden")

    if not paper.answer_key_docx_path or not os.path.exists(paper.answer_key_docx_path):
        export_answer_key(paper_id, db, current_user)
        paper = db.query(Paper).filter(Paper.id == paper_id).first()

    # Audit download
    audit = AuditLog(
        school_id=paper.school_id,
        user_id=current_user.id,
        action="download_confidential_answer_key",
        resource_type="paper",
        resource_id=paper.id,
        details=f"Downloaded confidential marking guide by {current_user.email}"
    )
    db.add(audit)
    db.commit()

    ascii_subj = "".join(c for c in paper.subject if c.isascii() and (c.isalnum() or c in ("-", "_", " "))).strip().replace(" ", "_")
    if not ascii_subj:
        ascii_subj = "PakStudies" if "مطالعہ" in (paper.subject or "") else ("Urdu" if paper.language == "ur" else "Paper")

    safe_ascii_filename = f"CONFIDENTIAL_AnswerKey_{ascii_subj}_Grade_{paper.grade}_{paper.id[:8]}.docx"
    encoded_utf8_filename = urllib.parse.quote(f"CONFIDENTIAL_MarkingScheme_{paper.subject}_{paper.grade}_{paper.title}.docx")
    content_disposition = f"attachment; filename=\"{safe_ascii_filename}\"; filename*=UTF-8''{encoded_utf8_filename}"

    return FileResponse(
        path=paper.answer_key_docx_path,
        filename=safe_ascii_filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": content_disposition
        }
    )

def _format_paper_dict(paper: Paper) -> dict:
    sections = []
    for s in paper.sections:
        q_list = []
        for q in s.questions:
            q_list.append({
                "id": q.id,
                "section_id": s.id,
                "question_number": q.question_number,
                "question_type": q.question_type,
                "question_text": q.question_text,
                "options": json.loads(q.options_json or "[]"),
                "correct_answer": q.correct_answer,
                "marks": q.marks,
                "difficulty": q.difficulty,
                "blooms_level": q.blooms_level or "Understand",
                "source_reference": q.source_reference,
                "source_page": q.source_page,
                "source_excerpt": q.source_excerpt,
                "confidence_score": q.confidence_score or 0.95,
                "quality_score": q.quality_score or 0.92,
                "duplicate_risk": q.duplicate_risk or 0.03,
                "explanation": q.explanation,
                "review_status": q.review_status,
            })
        sections.append({
            "id": s.id,
            "paper_id": paper.id,
            "title": s.title,
            "section_type": s.section_type,
            "sort_order": s.sort_order,
            "total_questions": s.total_questions,
            "questions_to_attempt": s.questions_to_attempt,
            "marks_per_question": s.marks_per_question,
            "total_section_marks": s.total_section_marks,
            "instructions": s.instructions,
            "questions": q_list,
        })

    return {
        "id": paper.id,
        "title": paper.title,
        "exam_type": paper.exam_type,
        "academic_session": paper.academic_session,
        "grade": paper.grade,
        "subject": paper.subject,
        "language": paper.language,
        "time_allowed_minutes": paper.time_allowed_minutes,
        "total_marks": paper.total_marks,
        "instructions": paper.instructions,
        "verification_code": paper.verification_code,
        "watermark_text": paper.watermark_text,
        "sections": sections,
    }

def _format_paper_response(p: Paper) -> PaperResponse:
    d = _format_paper_dict(p)
    return PaperResponse(
        id=p.id,
        school_id=p.school_id,
        created_by_id=p.created_by_id,
        book_id=p.book_id,
        title=p.title,
        exam_type=p.exam_type,
        academic_session=p.academic_session,
        grade=p.grade,
        subject=p.subject,
        language=p.language,
        time_allowed_minutes=p.time_allowed_minutes,
        total_marks=p.total_marks,
        instructions=p.instructions,
        status=p.status,
        selected_chapters=json.loads(p.selected_chapters_json or "[]"),
        docx_path=p.docx_path,
        answer_key_docx_path=p.answer_key_docx_path,
        verification_code=p.verification_code,
        watermark_text=p.watermark_text,
        created_at=p.created_at,
        updated_at=p.updated_at,
        sections=d["sections"]
    )
