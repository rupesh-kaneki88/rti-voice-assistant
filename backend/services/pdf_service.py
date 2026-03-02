"""
PDF Generation service for RTI applications
"""
import logging
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import io

logger = logging.getLogger(__name__)


class PDFService:
    """Service for generating RTI application PDFs"""
    
    def generate_rti_pdf(self, form_data: dict, session_id: str) -> bytes:
        """
        Generate RTI application PDF
        
        Args:
            form_data: Form data dictionary
            session_id: Session ID
            
        Returns:
            PDF bytes
        """
        try:
            # Create PDF buffer
            buffer = io.BytesIO()
            
            # Create PDF document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18,
            )
            
            # Container for PDF elements
            elements = []
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor('#1e40af'),
                spaceAfter=30,
                alignment=1  # Center
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=colors.HexColor('#1e40af'),
                spaceAfter=12,
            )
            
            normal_style = styles['Normal']
            normal_style.fontSize = 10
            normal_style.leading = 14
            
            # Title
            title = Paragraph("APPLICATION UNDER RIGHT TO INFORMATION ACT, 2005", title_style)
            elements.append(title)
            elements.append(Spacer(1, 0.2*inch))
            
            # Application details
            app_date = datetime.now().strftime("%d/%m/%Y")
            app_number = f"RTI-{session_id[:8].upper()}"
            
            details_data = [
                ['Application Number:', app_number],
                ['Date of Application:', app_date],
            ]
            
            details_table = Table(details_data, colWidths=[2*inch, 4*inch])
            details_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            elements.append(details_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Applicant Information
            elements.append(Paragraph("APPLICANT INFORMATION", heading_style))
            
            applicant_data = [
                ['Name:', form_data.get('applicant_name', 'Not provided')],
                ['Address:', form_data.get('address', 'Not provided')],
            ]
            
            applicant_table = Table(applicant_data, colWidths=[1.5*inch, 4.5*inch])
            applicant_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            elements.append(applicant_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Department Information
            elements.append(Paragraph("DEPARTMENT INFORMATION", heading_style))
            
            dept_text = form_data.get('department', 'Not specified')
            dept_para = Paragraph(f"<b>To:</b> {dept_text}", normal_style)
            elements.append(dept_para)
            elements.append(Spacer(1, 0.3*inch))
            
            # Information Sought
            elements.append(Paragraph("INFORMATION SOUGHT", heading_style))
            
            info_text = form_data.get('information_sought', 'Not provided')
            info_para = Paragraph(info_text, normal_style)
            elements.append(info_para)
            elements.append(Spacer(1, 0.3*inch))
            
            # Reason (if provided)
            if form_data.get('reason'):
                elements.append(Paragraph("REASON FOR SEEKING INFORMATION", heading_style))
                reason_para = Paragraph(form_data.get('reason'), normal_style)
                elements.append(reason_para)
                elements.append(Spacer(1, 0.3*inch))
            
            # Declaration
            elements.append(Spacer(1, 0.3*inch))
            elements.append(Paragraph("DECLARATION", heading_style))
            
            declaration_text = """
            I hereby declare that the information sought does not fall within the restrictions 
            contained in Section 8 and 9 of the RTI Act, 2005 and to the best of my knowledge 
            it pertains to your office.
            """
            declaration_para = Paragraph(declaration_text, normal_style)
            elements.append(declaration_para)
            
            # Signature section
            elements.append(Spacer(1, 0.5*inch))
            
            signature_data = [
                ['Date: ' + app_date, 'Signature of Applicant'],
                ['', ''],
                ['', '(To be signed at the time of submission)'],
            ]
            
            signature_table = Table(signature_data, colWidths=[3*inch, 3*inch])
            signature_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTSIZE', (1, 2), (1, 2), 8),
                ('TEXTCOLOR', (1, 2), (1, 2), colors.grey),
            ]))
            
            elements.append(signature_table)
            
            # Footer
            elements.append(Spacer(1, 0.5*inch))
            footer_text = """
            <i>Note: This application is generated electronically using the RTI Voice Assistant. 
            Please submit this application to the concerned Public Information Officer (PIO) 
            of the department mentioned above.</i>
            """
            footer_para = Paragraph(footer_text, normal_style)
            elements.append(footer_para)
            
            # Build PDF
            doc.build(elements)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            logger.info(f"PDF generated successfully: {len(pdf_bytes)} bytes")
            
            return pdf_bytes
        
        except Exception as e:
            logger.error(f"PDF generation error: {e}", exc_info=True)
            raise
