"""
Utility functions for grade calculation and PDF report generation.
"""

from decimal import Decimal
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def calculate_average(internal1, internal2):
    """Calculate average of two internal assessment marks."""
    return (Decimal(str(internal1)) + Decimal(str(internal2))) / 2


def calculate_grade(average):
    """
    Assign grade based on average marks.
    90-100 → O, 80-89 → A+, 70-79 → A, 60-69 → B+, 50-59 → B, Below 50 → RA
    """
    avg = float(average)
    if avg >= 90:
        return 'O'
    if avg >= 80:
        return 'A+'
    if avg >= 70:
        return 'A'
    if avg >= 60:
        return 'B+'
    if avg >= 50:
        return 'B'
    return 'RA'


def generate_subject_pdf(student, mark):
    """
    Generate a PDF report for a single subject's marks (Student + Subject).
    Returns BytesIO buffer containing the PDF.
    """
    return generate_student_pdf(student, [mark], subject_name=mark.subject.subject_name)


def generate_student_pdf(student, marks_list, subject_name=None):
    """
    Generate a PDF report for a student's academic results.
    When subject_name is provided, the report covers a single subject only.
    Returns BytesIO buffer containing the PDF.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=6,
        alignment=1,
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=20,
        alignment=1,
    )
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e40af'),
        spaceBefore=16,
        spaceAfter=10,
    )

    elements = []

    # College header
    elements.append(Paragraph('College ERP', title_style))
    report_title = (
        f'{subject_name} — Internal Marks Report'
        if subject_name
        else 'Student Internal Marks and Attendance Report'
    )
    elements.append(Paragraph(report_title, subtitle_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Student information
    elements.append(Paragraph('Student Information', heading_style))
    student_data = [
        ['Roll Number', student.roll_number],
        ['Student Name', student.name],
        ['Department', student.department],
        ['Year', student.year],
    ]
    student_table = Table(student_data, colWidths=[2 * inch, 4 * inch])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#dbeafe')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#93c5fd')),
    ]))
    elements.append(student_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Marks table
    elements.append(Paragraph('Academic Results', heading_style))
    marks_header = [
        'Subject', 'Internal 1', 'Internal 2', 'Attendance',
        'Average', 'Grade', 'Teacher',
    ]
    marks_rows = [marks_header]
    for mark in marks_list:
        marks_rows.append([
            mark.subject.subject_name,
            str(mark.internal1),
            str(mark.internal2),
            f"{mark.attendance}%",
            str(mark.average),
            mark.grade,
            mark.teacher.name,
        ])

    marks_table = Table(
        marks_rows,
        colWidths=[1.2 * inch, 0.8 * inch, 0.8 * inch, 0.9 * inch,
                   0.8 * inch, 0.6 * inch, 1.2 * inch],
    )
    marks_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#93c5fd')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f9ff')]),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(marks_table)

    # Footer with generated date
    from django.utils import timezone
    elements.append(Spacer(1, 0.5 * inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#64748b'),
        alignment=2,
    )
    generated_date = timezone.now().strftime('%B %d, %Y')
    elements.append(Paragraph(f'Generated on: {generated_date}', footer_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer
