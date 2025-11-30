"""
Report generation utilities for HTML and PDF
"""
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def generate_doctor_report_html(report_data):
    """
    Generate HTML report for doctor monthly activity
    """
    try:
        doctor = report_data['doctor']
        period = report_data['period']
        stats = report_data['statistics']
        appointments = report_data['appointments']
        treatments = report_data['treatments']
        diagnosis_summary = report_data.get('diagnosis_summary', {})
        
        month_name = datetime(int(period['year']), int(period['month']), 1).strftime('%B %Y')
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Monthly Activity Report - {month_name}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            color: #333;
        }}
        .header {{
            background-color: #4CAF50;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0;
        }}
        .section {{
            margin-bottom: 30px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }}
        .section h2 {{
            color: #4CAF50;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .statistics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .stat-card {{
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-card h3 {{
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
        }}
        .stat-card .value {{
            font-size: 32px;
            font-weight: bold;
            color: #4CAF50;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .footer {{
            margin-top: 30px;
            padding: 15px;
            text-align: center;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Monthly Activity Report</h1>
        <p>Dr. {doctor['first_name']} {doctor['last_name']} - {month_name}</p>
    </div>
    
    <div class="section">
        <h2>Statistics Summary</h2>
        <div class="statistics">
            <div class="stat-card">
                <h3>Total Appointments</h3>
                <div class="value">{stats['total_appointments']}</div>
            </div>
            <div class="stat-card">
                <h3>Completed</h3>
                <div class="value">{stats['completed']}</div>
            </div>
            <div class="stat-card">
                <h3>Cancelled</h3>
                <div class="value">{stats['cancelled']}</div>
            </div>
            <div class="stat-card">
                <h3>Unique Patients</h3>
                <div class="value">{stats['unique_patients']}</div>
            </div>
            <div class="stat-card">
                <h3>Treatments Provided</h3>
                <div class="value">{stats['treatments_provided']}</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>Appointments ({len(appointments)})</h2>
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Patient</th>
                    <th>Status</th>
                    <th>Reason</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for apt in appointments[:50]:  # Limit to first 50 for display
            html += f"""
                <tr>
                    <td>{apt.get('appointment_date', 'N/A')}</td>
                    <td>{apt.get('appointment_time', 'N/A')}</td>
                    <td>{apt.get('patient_name', 'N/A')}</td>
                    <td>{apt.get('status', 'N/A')}</td>
                    <td>{apt.get('reason', 'N/A')[:50] if apt.get('reason') else 'N/A'}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
    </div>
"""
        
        if diagnosis_summary:
            html += """
    <div class="section">
        <h2>Diagnosis Summary</h2>
        <table>
            <thead>
                <tr>
                    <th>Diagnosis</th>
                    <th>Count</th>
                </tr>
            </thead>
            <tbody>
"""
            for diagnosis, count in sorted(diagnosis_summary.items(), key=lambda x: x[1], reverse=True):
                html += f"""
                <tr>
                    <td>{diagnosis}</td>
                    <td>{count}</td>
                </tr>
"""
            html += """
            </tbody>
        </table>
    </div>
"""
        
        html += f"""
    <div class="footer">
        <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        <p>Hospital Management System</p>
    </div>
</body>
</html>
"""
        
        return html
        
    except Exception as e:
        logger.error(f"Error generating HTML report: {str(e)}")
        return f"<html><body><h1>Error generating report: {str(e)}</h1></body></html>"

def generate_doctor_report_pdf(report_data, doctor_id, month, year):
    """
    Generate PDF report for doctor monthly activity
    Requires reportlab library
    """
    try:
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
        except ImportError:
            logger.warning("reportlab not installed. PDF generation disabled.")
            return None
        
        # Create PDF file path
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        filename = f"doctor_{doctor_id}_report_{year}_{month:02d}.pdf"
        filepath = os.path.join(reports_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(f"Monthly Activity Report - {datetime(year, month, 1).strftime('%B %Y')}", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Doctor info
        doctor = report_data['doctor']
        doctor_info = Paragraph(f"Dr. {doctor['first_name']} {doctor['last_name']}", styles['Heading2'])
        story.append(doctor_info)
        story.append(Spacer(1, 0.2*inch))
        
        # Statistics
        stats = report_data['statistics']
        stats_data = [
            ['Metric', 'Value'],
            ['Total Appointments', str(stats['total_appointments'])],
            ['Completed', str(stats['completed'])],
            ['Cancelled', str(stats['cancelled'])],
            ['Unique Patients', str(stats['unique_patients'])],
            ['Treatments Provided', str(stats['treatments_provided'])]
        ]
        
        stats_table = Table(stats_data)
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"PDF report generated: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error generating PDF report: {str(e)}")
        return None

