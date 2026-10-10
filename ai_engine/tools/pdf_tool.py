import re
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)


def clean_for_reportlab(text):
    if not text:
        return ""
    if isinstance(text, dict):
        parts = []
        if text.get('analysis_markdown'):
            parts.append(str(text['analysis_markdown']))
        if text.get('matching_skills'):
            skills = text['matching_skills']
            if isinstance(skills, list):
                skills = ", ".join(skills)
            parts.append(f"Matching Skills: {skills}")
        if text.get('missing_skills'):
            skills = text['missing_skills']
            if isinstance(skills, list):
                skills = ", ".join(skills)
            parts.append(f"Skills to Acquire: {skills}")
        text = "\n".join(parts) if parts else str(text)

    text = str(text)
    # Remove raw dict keys if present in string representation
    text = (
        text.replace("analysis_markdown:", "")
        .replace("match_percentage:", "")
        .replace("matching_skills:", "")
        .replace("missing_skills:", "")
    )
    # Replace ₹ with Rs. to prevent black box in Helvetica font
    text = text.replace("₹", "Rs. ")
    # Convert markdown **bold** to <b>bold</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Replace newlines with breaks
    text = text.replace('\n', '<br/>')
    return text.strip()


def _overall_feasibility_label(score):
    """Map overall validation score to a human-readable feasibility label."""
    try:
        s = float(score)
    except (TypeError, ValueError):
        return "Moderate Feasibility"
    if s >= 90:
        return "Excellent Feasibility"
    elif s >= 80:
        return "High Feasibility"
    elif s >= 65:
        return "Moderate Feasibility"
    elif s >= 50:
        return "Low Feasibility"
    else:
        return "Needs Improvement"


def generate_pdf_report(startup_data, output_filepath):
    """
    Generates a professional PDF Startup Intelligence Report using ReportLab.
    """
    path = Path(output_filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=12
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=colors.HexColor('#2563EB'),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#334155')
    )

    story = []

    # Title Banner
    startup_name = startup_data.get('startup_name', 'Student Startup Project')
    domain = startup_data.get('domain', 'Technology')
    story.append(Paragraph(
        "STUDENT STARTUP PROPOSAL & INTEL REPORT (TAMIL NADU, INDIA)",
        subtitle_style
    ))
    story.append(Paragraph(
        f"{clean_for_reportlab(startup_name).upper()}",
        title_style
    ))
    story.append(Paragraph(
        f"<b>Domain:</b> {clean_for_reportlab(domain)} &nbsp;|&nbsp; "
        "<b>Location:</b> Tamil Nadu, India &nbsp;|&nbsp; "
        "<b>Engine:</b> Autonomous Multi-Agent AI Pipeline",
        subtitle_style
    ))
    story.append(HRFlowable(
        width="100%", thickness=2.5,
        color=colors.HexColor('#2563EB'), spaceAfter=12
    ))

    # Executive Summary Section with Multiple Recommended Tech Stacks
    story.append(Paragraph(
        "1. Executive Summary & Recommended Technology Stacks",
        section_heading
    ))
    problem = clean_for_reportlab(startup_data.get(
        'problem', 'Identified industry problem statement.'
    ))
    solution = clean_for_reportlab(startup_data.get(
        'solution', 'Proposed AI-driven solution.'
    ))
    user_tech = clean_for_reportlab(startup_data.get(
        'technology', ''
    )).strip()
    target = clean_for_reportlab(startup_data.get(
        'target_customer', 'Student entrepreneurs, farmers & SMBs'
    ))

    tech_stack_details = (
        "<b>Multiple Recommended Tech Stacks for Implementation:</b><br/>"
        "• <b>Option 1: Production Web Stack (Recommended)</b> — Frontend: "
        "React.js | Backend: Python Flask REST API | AI Engine: Google Gemini "
        "API | DB: MongoDB | Hosting: Render/Vercel<br/>"
        "• <b>Option 2: Mobile-First Native Stack</b> — App: Flutter / React "
        "Native | Backend: Node.js / Python API | Cloud: Firebase Auth & "
        "Firestore | ML: MobileNet / Edge ML<br/>"
        "• <b>Option 3: Enterprise Scalable Stack</b> — Frontend: Next.js | "
        "Architecture: Microservices | DB: PostgreSQL + Redis | Vector DB: "
        "LangChain + ChromaDB"
    )
    ignored_techs = ['any modern stack', 'python, web', 'python', 't']
    if user_tech and user_tech.lower() not in ignored_techs:
        tech_stack_details = (
            f"<b>User Provided Tech:</b> {user_tech}<br/><br/>"
            + tech_stack_details
        )

    story.append(Paragraph(f"<b>Problem:</b> {problem}", body_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Solution:</b> {solution}", body_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"<b>Target Customer Base:</b> {target}", body_style
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(tech_stack_details, body_style))
    story.append(Spacer(1, 10))

    # Validation Score Table
    val = startup_data.get('validation', {})
    story.append(Paragraph(
        "2. Feasibility & Validation Breakdown (Academic Guide Rationale)",
        section_heading
    ))
    story.append(Paragraph(
        "<b>Score Calculation Rationale for Project Guide:</b><br/>"
        "<code>Overall Score = (Innovation × 25%) + (Market Demand × 30%) + "
        "(Technical Feasibility × 25%) + (Business Margins × 20%)</code>",
        body_style
    ))
    story.append(Spacer(1, 6))

    val_data = [
        ['Parameter', 'Weight', 'Score', 'Status / Feasibility'],
        ['Innovation Uniqueness', '25%',
         f"{val.get('innovation_score', 90)}/100", 'High Uniqueness'],
        ['Market Customer Demand', '30%',
         f"{val.get('market_score', 85)}/100", 'High Market Demand'],
        ['Technical Feasibility', '25%',
         f"{val.get('technology_score', 80)}/100", 'Technically Feasible'],
        ['Business Profitability', '20%',
         f"{val.get('business_score', 88)}/100", 'Strong Profit Margins'],
        ['OVERALL VALIDATION SCORE', '100%',
         f"{val.get('overall_score', 86)}/100",
         _overall_feasibility_label(val.get('overall_score', 86))]
    ]

    val_table = Table(val_data, colWidths=[180, 70, 90, 160])
    val_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#EFF6FF')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#1E40AF')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    story.append(val_table)
    story.append(Spacer(1, 10))

    # Business Model Canvas Overview
    bm = startup_data.get('business_model', {})
    story.append(Paragraph(
        "3. Business Model Canvas Overview (9-Block Strategic Plan)",
        section_heading
    ))
    val_prop = clean_for_reportlab(bm.get(
        'value_proposition', 'AI automated guidance and market validation.'
    ))
    cust_seg = clean_for_reportlab(bm.get(
        'customer_segments',
        'Engineering students, incubators & early founders in India.'
    ))
    rev_str = clean_for_reportlab(bm.get(
        'revenue_streams',
        'Freemium model, premium reports (Rs. 499/report), B2B subscriptions.'
    ))
    channels = clean_for_reportlab(bm.get(
        'channels',
        'Direct Web App, Campus Ambassadors in Tamil Nadu Colleges.'
    ))
    resources = clean_for_reportlab(bm.get(
        'key_resources', 'AI Models, Vector Knowledge Base, Web App Backend'
    ))
    costs = clean_for_reportlab(bm.get(
        'cost_structure',
        'Cloud AI API tokens, server hosting, ongoing platform maintenance.'
    ))

    bm_text = f"""
    <b>Value Proposition:</b> {val_prop}<br/>
    <b>Customer Segments:</b> {cust_seg}<br/>
    <b>Revenue Streams:</b> {rev_str}<br/>
    <b>Channels:</b> {channels}<br/>
    <b>Key Resources:</b> {resources}<br/>
    <b>Cost Structure:</b> {costs}
    """
    story.append(Paragraph(bm_text, body_style))
    story.append(Spacer(1, 10))

    # Financial Analysis Table in INR (Rs.)
    fin = startup_data.get('financials', {})
    dev_c = fin.get('development_cost', 150000)
    mkt_c = fin.get('marketing_cost', 50000)
    op_c = fin.get('operational_cost', 30000)
    rev_p = fin.get('revenue_prediction', 650000)
    prof_e = fin.get('profit_estimate', 420000)
    be_period = clean_for_reportlab(fin.get('break_even_period', '7 Months'))

    story.append(Paragraph(
        "4. Financial Estimates & ROI Projection (in Indian Rupees - Rs.)",
        section_heading
    ))
    fin_data = [
        ['Financial Metric', 'Estimated Amount (Rs.)'],
        ['Initial Development Cost', f"Rs. {dev_c:,.2f}"],
        ['Marketing & Acquisition Cost', f"Rs. {mkt_c:,.2f}"],
        ['Annual Operational Expenses', f"Rs. {op_c:,.2f}"],
        ['Projected Annual Revenue', f"Rs. {rev_p:,.2f}"],
        ['Estimated Net Profit', f"Rs. {prof_e:,.2f}"],
        ['Return on Investment (ROI)', f"{fin.get('roi', 182.6)}%"],
        ['Break-Even Horizon', f"{be_period}"]
    ]

    fin_table = Table(fin_data, colWidths=[240, 260])
    fin_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FAFAFA')),
    ]))
    story.append(fin_table)
    story.append(Spacer(1, 10))

    # Recommendations & Tamil Nadu Ecosystem Opportunities
    story.append(Paragraph(
        "5. Strategic Recommendations & Tamil Nadu Funding Schemes",
        section_heading
    ))
    swot = startup_data.get('swot_analysis', '')
    if swot:
        story.append(Paragraph(clean_for_reportlab(swot), body_style))
    else:
        tn_schemes = (
            "<b>Funding Opportunities for Tamil Nadu Entrepreneurs:</b><br/>"
            "• <b>StartupTN TanSEED Grant:</b> Up to Rs. 10 Lakhs grant.<br/>"
            "• <b>EDII-TN IVP Programme:</b> IVP A (Rs. 2L) & IVP B (Rs. 5L)."
            "• <b>TANSIM & Startup India:</b> Incubation support & SISFS."
        )
        story.append(Paragraph(tn_schemes, body_style))

    story.append(Spacer(1, 10))

    # Skill Gap & Tech Stack Recommendations
    story.append(Paragraph(
        "6. Skill Gap Analysis & Development Roadmap", section_heading
    ))
    skill_gap = startup_data.get('skill_gap', '')
    if skill_gap:
        story.append(Paragraph(clean_for_reportlab(skill_gap), body_style))
    else:
        story.append(Paragraph(
            "Recommended Skill Development: Acquire Python REST API design, "
            "MongoDB integration, and Gemini AI agent fine-tuning.",
            body_style
        ))

    doc.build(story)
    return str(path)
