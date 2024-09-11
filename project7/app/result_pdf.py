from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.units import inch

def create_result_pdf(student_info, exam_info, marks_obtained):
    pdf = SimpleDocTemplate('result.pdf',pagesize=A4)

    elements = []

    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['BodyText']

    title =Paragraph("Result Report", title_style)
    elements.append(title)

    student_details = f"""
       <b>Student Name:</b> {student_info['name']}<br/>
       <b>Student ID:</b> {student_info['id']}<br/>
       <b>Class:</b> {student_info['class']}
    """

    student_paragraph = Paragraph(student_details,normal_style)
    elements.append(student_paragraph)

    exam_details = f"""
        <b>Exam:</b> {exam_info['name']}<br/>
        <b>Exam ID:</b> {exam_info['id']}<br/>
        <b>Total Marks:</b> {exam_info['total_marks']}
    """ 

    exam_paragraph = Paragraph(exam_details, normal_style)
    elements.append(exam_paragraph)

    # Create data for the table
    data = [['Subject', 'Marks', 'Grade']]
    total_marks = 0
    for mark in marks_obtained:
        data.append([mark['subject'], mark['marks'],  mark['grade']])
        total_marks += int(mark['marks'])
        
    data.append(['Total', f'{total_marks}'])
    data.append(['Grade', '', 'A+'])
    # Create the table
    column_widths = [ 2.5 * inch, 1.5 * inch, 2 * inch]

    table = Table(data, colWidths=column_widths)

    # Add style to the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),  # Body rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),

         # Style for the last row (total)
        ('BACKGROUND', (0, -2), (-1, -2), colors.grey),
        ('TEXTCOLOR', (0, -2), (-1, -2), colors.whitesmoke),
        ('FONTNAME', (0, -2), (-1, -2), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.grey),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ])

    table.setStyle(style)

    # # Add the table to the elements
    elements.append(table) 
    # Save the PDF
    pdf.build(elements)

    
student_info = {
    'name': 'John Doe',
    'id': '123456',
    'class': '10th Grade'
}

exam_info = {
    'name': 'Final Exam',
    'id': '987654',
    'total_marks': '500'
}

marks_obtained = [
    {'subject': 'Math', 'marks': '90', 'grade':'A'},
    {'subject': 'Science', 'marks': '85', 'grade':'B'},
    {'subject': 'English', 'marks': '88', 'grade':'C'},
    {'subject': 'History', 'marks': '92', 'grade':'D'},
    {'subject': 'Geography', 'marks': '89', 'grade':'E'},
]
create_result_pdf( student_info, exam_info, marks_obtained)
