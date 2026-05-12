"""
FastAPI router for PDF report generation
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime, date
from database import get_db
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ReportRequest(BaseModel):
    title: str = "AI Workforce Intelligence Report"
    include_attrition: bool = True
    include_overtime: bool = True
    include_optimization: bool = True

@router.post("/generate-pdf")
async def generate_pdf_report(request: ReportRequest, db: Session = Depends(get_db)):
    """
    Generate comprehensive PDF report with charts and analytics
    """
    try:
        # Create reports directory
        os.makedirs("./reports", exist_ok=True)
        
        filename = f"workforce_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = f"./reports/{filename}"
        
        # Create PDF
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title Page
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a73e8'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        elements.append(Spacer(1, 2*inch))
        elements.append(Paragraph(request.title, title_style))
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("AI Workforce Intelligence & Shift Optimization Platform", styles['Normal']))
        elements.append(PageBreak())
        
        # Executive Summary
        elements.append(Paragraph("Executive Summary", styles['Heading1']))
        elements.append(Spacer(1, 0.2*inch))
        
        summary_text = """
        This report provides comprehensive insights into workforce management, including:
        • Attrition risk analysis and predictions
        • Overtime cost analysis and optimization opportunities
        • Shift scheduling optimization results
        • Department performance metrics
        • Strategic recommendations for workforce improvement
        """
        elements.append(Paragraph(summary_text, styles['Normal']))
        elements.append(Spacer(1, 0.5*inch))
        
        # Attrition Section
        if request.include_attrition:
            elements.append(Paragraph("1. Attrition Risk Analysis", styles['Heading2']))
            elements.append(Spacer(1, 0.2*inch))
            
            # Sample data (in production, query from database)
            attrition_data = [
                ['Risk Level', 'Employee Count', 'Percentage'],
                ['High Risk', '15', '12.5%'],
                ['Medium Risk', '35', '29.2%'],
                ['Low Risk', '70', '58.3%']
            ]
            
            t = Table(attrition_data, colWidths=[2*inch, 2*inch, 2*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(t)
            elements.append(Spacer(1, 0.5*inch))
            
            # Generate pie chart
            pie_chart_path = "./reports/attrition_chart.png"
            plt.figure(figsize=(6, 4))
            sizes = [15, 35, 70]
            labels = ['High Risk', 'Medium Risk', 'Low Risk']
            colors_pie = ['#ff6b6b', '#ffd93d', '#6bcf7f']
            plt.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%', startangle=90)
            plt.title('Attrition Risk Distribution')
            plt.savefig(pie_chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            elements.append(Image(pie_chart_path, width=4*inch, height=3*inch))
            elements.append(Spacer(1, 0.3*inch))
        
        # Overtime Section
        if request.include_overtime:
            elements.append(Paragraph("2. Overtime Cost Analysis", styles['Heading2']))
            elements.append(Spacer(1, 0.2*inch))
            
            overtime_data = [
                ['Department', 'Total OT Hours', 'OT Cost'],
                ['Manufacturing', '450', '$13,500'],
                ['Healthcare', '380', '$15,200'],
                ['Warehouse', '220', '$6,600'],
                ['Quality Control', '150', '$4,500']
            ]
            
            t = Table(overtime_data, colWidths=[2.5*inch, 1.75*inch, 1.75*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue)
            ]))
            elements.append(t)
            elements.append(Spacer(1, 0.3*inch))
            
            # Bar chart
            bar_chart_path = "./reports/overtime_chart.png"
            departments = ['Manufacturing', 'Healthcare', 'Warehouse', 'QC']
            hours = [450, 380, 220, 150]
            
            plt.figure(figsize=(7, 4))
            plt.bar(departments, hours, color='#4a90e2')
            plt.xlabel('Department')
            plt.ylabel('Overtime Hours')
            plt.title('Overtime Hours by Department')
            plt.xticks(rotation=15)
            plt.tight_layout()
            plt.savefig(bar_chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            elements.append(Image(bar_chart_path, width=5*inch, height=3*inch))
            elements.append(Spacer(1, 0.3*inch))
        
        # Recommendations
        elements.append(PageBreak())
        elements.append(Paragraph("3. Strategic Recommendations", styles['Heading2']))
        elements.append(Spacer(1, 0.2*inch))
        
        recommendations = """
        <b>1. Attrition Reduction:</b><br/>
        • Implement retention programs for high-risk employees<br/>
        • Conduct stay interviews quarterly<br/>
        • Review compensation for at-risk departments<br/>
        <br/>
        <b>2. Overtime Optimization:</b><br/>
        • Hire 5-7 additional workers to reduce overtime by 30%<br/>
        • Implement flex scheduling<br/>
        • Cross-train employees for multi-role coverage<br/>
        <br/>
        <b>3. Shift Optimization:</b><br/>
        • Use AI-powered shift scheduling to reduce costs by 20%<br/>
        • Ensure 12-hour rest periods between shifts<br/>
        • Limit consecutive night shifts to 2-3<br/>
        <br/>
        <b>4. Employee Wellness:</b><br/>
        • Introduce fatigue management program<br/>
        • Provide mental health support<br/>
        • Rotate difficult shifts fairly
        """
        
        elements.append(Paragraph(recommendations, styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        
        logger.info(f"PDF report generated: {filepath}")
        
        return FileResponse(
            filepath,
            media_type='application/pdf',
            filename=filename
        )
        
    except Exception as e:
        logger.error(f"PDF generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_reports():
    """
    List all generated reports
    """
    reports_dir = "./reports"
    if not os.path.exists(reports_dir):
        return {'reports': []}
    
    files = [f for f in os.listdir(reports_dir) if f.endswith('.pdf')]
    reports = []
    
    for file in files:
        filepath = os.path.join(reports_dir, file)
        stats = os.stat(filepath)
        reports.append({
            'filename': file,
            'size_kb': round(stats.st_size / 1024, 2),
            'created': datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return {'reports': reports, 'count': len(reports)}
