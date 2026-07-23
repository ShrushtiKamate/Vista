print("🔥 FASTAPI FILE IS BEING IMPORTED")
import os
print("🔥 RUNNING FILE:", os.path.abspath(__file__))
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mongoengine import connect, Document, StringField, FileField
import pdfplumber
import pandas as pd
import requests
from io import BytesIO
from fastapi.responses import StreamingResponse
from institute.models import mandatory_dis
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from google import genai
from reportlab.lib.units import inch
import requests
# import google.generativeai as genai
from mongoengine import Document, StringField, FileField

import google.generativeai as genai
import io
import spacy
import PyPDF2
import requests
import base64
import pandas as pd


app = FastAPI()

#connects our FastAPI application to the MongoDB database.
connect(
    db="nirikshan_db",
    host="127.0.0.1",
    port=27017
)


class excel_data(Document):
    college_name = StringField(required=True)
    intake = StringField(required=True)
    file_data = FileField()  # Field to store the processed Excel file

    meta={
        'collection':'excel_data'
    }

class CollegeLoginInfo(BaseModel):
    # college_name: str
    college_id: str
    intake: str

class compliancereport(Document):
    college_name = StringField(required=True)
    intake = StringField(required=True)
    report_file = FileField()
    
    meta = {
        'collection': 'compliance_reports'
    }

class DeficiencyReport(Document):
    college = StringField(required=True)
    branch = StringField(required=True)
    file = FileField()

    meta = {
        'collection': 'deficiency_report'
    }

class PatternReport(Document):
    filename = StringField(required=True)
    file = FileField()

    meta = {
        'collection': 'pattern_reports'
    }

@app.post("/process-mandatory-disclosure/")
async def process_mandatory_disclosure(info: CollegeLoginInfo):
    try:
        # Fetch mandatory disclosure based on college_name
       
        mandatory_disclosure = mandatory_dis.objects(
            college_name=info.college_id
        ).first()
        if not mandatory_disclosure:
            raise HTTPException(status_code=404, detail="Mandatory disclosure not found")

        # Read the PDF file from the database
        pdf_file = mandatory_disclosure.file.read()  # Read the file data

        # Keywords and associated sheet titles
        table_titles = {
            "Professor": "Faculty Information",
            "Classroom": "Classroom Details",
            "Laboratory": "Lab Information",
            "Course": "Courses Offered",
            "Intake": "Student Intake",
            "PCs": "PC Details",
            "titles": "Library Details",
        }

        # DataFrame to store extracted data
        tables_with_titles = []

        # Open the PDF and extract tables
        with pdfplumber.open(BytesIO(pdf_file)) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                try:
                    tables = page.extract_tables()
                    for table in tables:
                        # Convert table to DataFrame
                        df = pd.DataFrame(table)

                         # ✅ ADD HERE
                        print("\n📊 Extracted Table Preview:")
                        print(df.head())
                        print("\n---------------------------\n")
                        # Skip tables with fewer than 3 rows or columns
                        if df.shape[0] < 3 or df.shape[1] < 3:
                            continue
                        # Check if the table contains any of the keywords
                        for keyword, title in table_titles.items():
                            if df.astype(str).apply(lambda x: x.str.contains(keyword, case=False, na=False)).any().any():
                                # Skip large tables for specific titles
                                if title == "Courses Offered" and df.shape[0] > 20:
                                    continue
                                if title == "Library Details" and df.shape[0] > 20:
                                    continue
                                df["Source_Page"] = page_num  # Add source page number
                                tables_with_titles.append((df, title))
                                break
                except Exception as e:
                    print(f"Error on page {page_num}: {e}")

        # Save relevant tables to Excel
        if tables_with_titles:
            output_excel = BytesIO()
            with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
                title_counts = {}
                for table, title in tables_with_titles:
                    title_counts[title] = title_counts.get(title, 0) + 1
                    sheet_name = f"{title} ({title_counts[title]})" if title_counts[title] > 1 else title
                    table.to_excel(writer, sheet_name=sheet_name[:31], index=False, header=False)

            output_excel.seek(0)

            # Save the processed data to a new class in the database
            processed_data = excel_data(
                # college_name=info.college_name,
                college_name=info.college_id,
                intake =info.intake,
                file_data=output_excel.read()  # Store the Excel file data
            )
            processed_data.save()

            report_response = await create_compliance_report(info)
            return {
                "message": "Compliance report processed successfully",
                "report_response": report_response
            }
        else:
            raise HTTPException(status_code=404, detail="No relevant tables found.")

    except Exception as e:
        print("\n❌ ERROR IN PROCESS MANDATORY ❌\n")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/create-compliance-report/")     
async def create_compliance_report(info: CollegeLoginInfo):
    print("➡️ Generating report for:", info.college_id)
    try:
        # excel_file_obj = excel_data.objects(college_name=info.college_name).first()
        excel_file_obj = excel_data.objects(college_name=info.college_id).first()

        if not excel_file_obj:
            raise HTTPException(status_code=404, detail="Excel not found")

        # Convert stored file data to a file-like object
        excel_file = BytesIO(excel_file_obj.file_data.read())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # def analyze_faculty_data(excel_file):
    #     excel_data = pd.ExcelFile(excel_file)

    #     # Total professors analysis
    #     faculty_sheets = [sheet for sheet in excel_data.sheet_names if "Faculty Information" in sheet]
    #     total_professors = total_associate_professors = total_assistant_professors = 0

    #     for sheet_name in faculty_sheets:
    #         df = pd.read_excel(excel_file, sheet_name=sheet_name)
    #         if df.shape[1] < 3:
    #             continue
    #         third_column = df.iloc[:, 2].astype(str).str.strip().str.lower()
    #         for value in third_column:
    #             if value == "professor":
    #                 total_professors += 1
    #             elif value in {"associate professor", "asso.professor"}:
    #                 total_associate_professors += 1
    #             elif value in {"assistant professor", "asst professor", "asstt.professor"}:
    #                 total_assistant_professors += 1

    #     print(f"Total Professors: {total_professors}")
    #     print(f"Total Associate Professors: {total_associate_professors}")
    #     print(f"Total Assistant Professors: {total_assistant_professors}")

    #     return total_professors, total_associate_professors, total_assistant_professors
    
    def analyze_faculty_data(excel_file):
        excel_file.seek(0)
        excel_obj = pd.ExcelFile(excel_file)

        faculty_sheets = [
            sheet for sheet in excel_obj.sheet_names
            if "Faculty Information" in sheet
        ]

        total_professors = 0
        total_associate_professors = 0
        total_assistant_professors = 0

        for sheet_name in faculty_sheets:
            excel_file.seek(0)

            df = pd.read_excel(
                excel_file,
                sheet_name=sheet_name,
                header=None
            )

            print("\n========== FACULTY SHEET ==========")
            print(df.head(20))
            print("===================================")

            # Search whole row instead of fixed column
            row_text = df.astype(str).apply(
                lambda x: " ".join(x),
                axis=1
            ).str.lower()

            total_professors += row_text.str.contains(
                r'\bprofessor\b',
                case=False,
                na=False
            ).sum()

            total_associate_professors += row_text.str.contains(
                r'associate professor|asso.professor',
                case=False,
                na=False
            ).sum()

            total_assistant_professors += row_text.str.contains(
                r'assistant professor|assistant prof|asst professor|asstt.professor',
                case=False,
                na=False
            ).sum()

        print("Total Professors:", total_professors)
        print("Total Associate Professors:",
            total_associate_professors)
        print("Total Assistant Professors:",
            total_assistant_professors)

        return (
            total_professors,
            total_associate_professors,
            total_assistant_professors
        )
    

    def analyze_classroom_data(excel_file):
        excel_data = pd.ExcelFile(excel_file)

        classroom_sheets = [sheet for sheet in excel_data.sheet_names if "Classroom Details" in sheet]
        total_labs = total_classrooms = total_dept_library = workshops = smart_classroom = 0

        for sheet_name in classroom_sheets:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            if df.shape[1] < 3:
                continue
            # third_column = df.iloc[:, 2].astype(str).str.lower()

            all_text = df.astype(str).apply(lambda x: " ".join(x), axis=1).str.lower()

            print("ROW TEXT VALUES:")
            print(all_text.head())

            # total_labs += third_column.str.contains(r'\blaboratory\b', na=False).sum()
            # total_classrooms += third_column.str.contains(r'\bclassroom\b', na=False).sum()
            # total_dept_library += third_column.str.contains(r'\bdept. library\b|\bdepartment library\b', na=False).sum()
            # workshops += third_column.str.contains(r'\bworkshop\b', na=False).sum()
            # smart_classroom += third_column.str.contains(r'\bsmart classroom\b', na=False).sum()

            total_labs += all_text.str.contains(r'lab|laboratory|laboratories', case=False, na=False).sum()

            total_classrooms += all_text.str.contains(
                r'\bclassroom\b|\bclassrooms\b',
                case=False,
                na=False
            ).sum()

            total_dept_library += all_text.str.contains(r'library', case=False, na=False).sum()

            workshops += all_text.str.contains(r'workshop', case=False, na=False).sum()

            smart_classroom += all_text.str.contains(r'smart classroom', case=False, na=False).sum()
        
        print(f"Total Labs: {total_labs}")
        print(f"Total Classrooms: {total_classrooms}")
        print(f"Total Dept Libraries: {total_dept_library}")
        print(f"Total Workshops: {workshops}")
        print(f"Total Smart Classrooms: {smart_classroom}")

        return total_labs, total_classrooms, total_dept_library, workshops, smart_classroom
    
    # def validate_classroom_details(excel_file):
    #     excel_data = pd.ExcelFile(excel_file)
        
    #     # Find sheets related to Classroom Details
    #     classroom_sheets = [sheet for sheet in excel_data.sheet_names if "Classroom Details" in sheet]
        
    #     validation_results = []
        
    #     for sheet_name in classroom_sheets:
    #         df = pd.read_excel(excel_file, sheet_name=sheet_name)
            
    #         # Ensure the DataFrame has at least 4 columns
    #         if df.shape[1] < 4:
    #             print(f"Error: '{sheet_name}' sheet has fewer than 4 columns.")
    #             continue
            
    #         # Iterate through the rows of the DataFrame
    #         for index, row in df.iterrows():
    #             third_col = str(row.iloc[2]).strip().lower()  # 3rd column
    #             fourth_col = row.iloc[3]  # 4th column (assumed numerical)
                
    #             # Default status
    #             status = "Valid"
                
    #             # Check conditions
    #             try:
    #                 if third_col in ["classroom", "laboratory", "smart classroom"]:
    #                     if fourth_col <= 66:
    #                         status = f"Invalid. The room is smaller by {66 - fourth_col} square meters"
    #                 elif third_col == "workshop":
    #                     if fourth_col <= 200:
    #                         status = f"Invalid. The room is smaller by {200 - fourth_col} square meters"
    #                 elif third_col == "tutorial":
    #                     if fourth_col <= 33:
    #                         status = f"Invalid. The room is smaller by {33 - fourth_col} square meters"
    #                 elif third_col == "seminar hall":
    #                     if fourth_col <= 132:
    #                         status = f"Invalid. The room is smaller by {132 - fourth_col} square meters"
    #             except Exception as e:
    #                 status = f"Error: {e}"
                
    #             # Append the result
    #             validation_results.append({
    #                 "Room Type (3rd Column)": row.iloc[2],
    #                 "Capacity (4th Column)": fourth_col,
    #                 "Status": status
    #             })
    #             print(validation_results)
    #             print(pd.DataFrame(validation_results))
    #     return pd.DataFrame(validation_results)



    def validate_classroom_details(excel_file):
        excel_file.seek(0)

        excel_obj = pd.ExcelFile(excel_file)

        classroom_sheets = [
            sheet for sheet in excel_obj.sheet_names
            if "Classroom Details" in sheet
        ]

        validation_results = []

        for sheet_name in classroom_sheets:
            excel_file.seek(0)

            df = pd.read_excel(
                excel_file,
                sheet_name=sheet_name,
                header=None
            )

            for _, row in df.iterrows():

                row_text = " ".join(
                    row.astype(str)
                ).lower()

                room_type = None

                if "smart classroom" in row_text:
                    room_type = "smart classroom"
                elif "classroom" in row_text:
                    room_type = "classroom"
                elif "lab" in row_text:
                    room_type = "laboratory"
                elif "workshop" in row_text:
                    room_type = "workshop"

                if not room_type:
                    continue

                numbers = [
                    x for x in row
                    if isinstance(x, (int, float))
                ]

                capacity = numbers[0] if numbers else 0

                status = "Valid"

                if room_type in [
                    "classroom",
                    "laboratory",
                    "smart classroom"
                ]:
                    if capacity < 66:
                        status = (
                            f"Invalid "
                            f"(Missing {66-capacity:.1f} sqm)"
                        )

                elif room_type == "workshop":
                    if capacity < 200:
                        status = (
                            f"Invalid "
                            f"(Missing {200-capacity:.1f} sqm)"
                        )

                validation_results.append({
                    "Room Type (3rd Column)": room_type,
                    "Capacity (4th Column)": capacity,
                    "Status": status
                })

        return pd.DataFrame(validation_results)

    def generate_report(faculty_data, infrastructure_data, validation_results=None, college_name=None, intake=None):
        try:
            # Create an in-memory PDF file
            output_pdf = BytesIO()
            doc = SimpleDocTemplate(output_pdf, pagesize=letter)
            elements = []  # List to hold all the content

            styles = getSampleStyleSheet()

            # Title Section
            title_style = styles['Title']
            title_style.fontName = 'Helvetica-Bold'
            title_style.fontSize = 16
            title = Paragraph("<b>Norms and Compliance with AICTE Norms</b>", title_style)
            elements.append(title)

            # Note Section
            note_style = styles['Normal']
            note_style.fontSize = 10
            note = Paragraph("<i>(Data taken from mandatory disclosure uploaded by college)</i>", note_style)
            elements.append(note)

            # Create faculty compliance table
            def create_faculty_compliance_table(elements, faculty_data):
                data = [
                    ['Faculty Category', 'Actual', 'Required', 'Compliance'],
                    ['Professor', faculty_data['professors'], faculty_data['required_professors'], faculty_data['professor_compliance']],
                    ['Associate Professor', faculty_data['associate_professors'], faculty_data['required_associate_professors'], faculty_data['associate_professor_compliance']],
                    ['Assistant Professor', faculty_data['assistant_professors'], faculty_data['required_assistant_professors'], faculty_data['assistant_professor_compliance']],
                ]

                table = Table(data, colWidths=[200, 100, 100, 100])
                table.setStyle(TableStyle([
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('BOX', (0, 0), (-1, -1), 1, colors.black)
                ]))

                for row_idx, row in enumerate(data[1:], start=1):
                    # if row[3].lower() != 'compliant':
                    #     table.setStyle(TableStyle([
                    #         ('BACKGROUND', (0, row_idx), (-1, row_idx), colors.red),
                    #     ]))

                    status = row[3].lower()

                    if status == 'compliant':  # YOUR RULE
                        table.setStyle(TableStyle([
                        ('BACKGROUND', (0, row_idx), (-1, row_idx), colors.red),
                        ('TEXTCOLOR', (0, row_idx), (-1, row_idx), colors.black)
                    ]))
                    else:  #  non-compliant
                        table.setStyle(TableStyle([
                        ('BACKGROUND', (0, row_idx), (-1, row_idx), colors.white),
                        ('TEXTCOLOR', (0, row_idx), (-1, row_idx), colors.black)
                    ]))

                elements.append(table)

            def markdown_to_formatted_paragraphs(markdown_text, styles):
                elements = []
                
                # Split the markdown into lines
                lines = markdown_text.split('\n')
                
                for line in lines:
                    # Headers
                    if line.startswith('# '):
                        elements.append(Paragraph(line.replace('# ', ''), styles['Title']))
                    elif line.startswith('## '):
                        elements.append(Paragraph(line.replace('## ', ''), styles['Heading2']))
                    elif line.startswith('### '):
                        elements.append(Paragraph(line.replace('### ', ''), styles['Heading3']))
                    
                    # Bold text
                    elif '**' in line:
                        formatted_line = line.replace('**', '<b>', 1).replace('**', '</b>', 1)
                        elements.append(Paragraph(formatted_line, styles['Normal']))
                    
                    # Italic text
                    elif '*' in line and line.count('*') == 2:
                        formatted_line = line.replace('*', '<i>', 1).replace('*', '</i>', 1)
                        elements.append(Paragraph(formatted_line, styles['Normal']))
                    
                    # Bullet points
                    elif line.startswith('- '):
                        formatted_line = line.replace('- ', '• ', 1)
                        elements.append(Paragraph(formatted_line, styles['Normal']))
                    
                    # Regular text
                    elif line.strip():
                        elements.append(Paragraph(line, styles['Normal']))
                
                return elements

            # Create infrastructure compliance table
            def create_infrastructure_compliance_table(elements, infrastructure_data):
                data = [
                    ['Infrastructure Category', 'Actual', 'Required', 'Compliance'],
                    ['Classrooms', infrastructure_data['classrooms'], infrastructure_data['required_classrooms'], infrastructure_data['classroom_compliance']],
                    ['Labs', infrastructure_data['labs'], infrastructure_data['required_labs'], infrastructure_data['lab_compliance']],
                    ['Workshops', infrastructure_data['workshops'], infrastructure_data['required_workshops'], infrastructure_data['workshop_compliance']],
                    ['Smart Classrooms', infrastructure_data['smart_classrooms'], infrastructure_data['required_smart_classrooms'], infrastructure_data['smart_classroom_compliance']],
                ]

                table = Table(data, colWidths=[200, 100, 100, 100])
                table.setStyle(TableStyle([
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('BOX', (0, 0), (-1, -1), 1, colors.black)
                ]))

                for row_idx, row in enumerate(data[1:], start=1):
                    # if row[3].lower() != 'compliant':
                    #     table.setStyle(TableStyle([
                    #         ('BACKGROUND', (0, row_idx), (-1, row_idx), colors.red),
                    #     ]))

                    status = row[3].lower()
                    if status == 'compliant':  # 🔴 YOUR RULE
                        table.setStyle(TableStyle([
                        ('BACKGROUND', (0, row_idx), (-1, row_idx), colors.red),
                        ('TEXTCOLOR', (0, row_idx), (-1, row_idx), colors.black)
                    ]))
                    else:  # ⚪ non-compliant
                        table.setStyle(TableStyle([
                        ('BACKGROUND', (0, row_idx), (-1, row_idx), colors.white),
                        ('TEXTCOLOR', (0, row_idx), (-1, row_idx), colors.black)
                    ]))

                elements.append(table)

            # Create classroom validation table
            def create_classroom_validation_table(elements, validation_results):
                if validation_results is None or validation_results.empty:
                    return

                # Convert validation results to a format suitable for PDF table
                data = [['Room Type', 'Capacity', 'Status']]
                for _, row in validation_results.iterrows():
                    data.append([
                        str(row['Room Type (3rd Column)']), 
                        str(row['Capacity (4th Column)']), 
                        str(row['Status'])
                    ])

                table = Table(data, colWidths=[200, 100, 200])
                table.setStyle(TableStyle([
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('BOX', (0, 0), (-1, -1), 1, colors.black)
                ]))

                # Highlight rows with invalid status
                for row_idx, row in enumerate(data[1:], start=1):
                    if 'Invalid' in str(row[2]):
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, row_idx), (-1, row_idx), colors.red),
                        ]))

                # Add a title for the validation results
                validation_title = Paragraph("<b>Classroom Space Validation Results</b>", styles['Heading2'])
                elements.append(validation_title)
                elements.append(table)

            # Add some spacing between sections
            elements.append(Spacer(1, 12))

            # Create tables
            create_faculty_compliance_table(elements, faculty_data)
            elements.append(Spacer(1, 12))
            create_infrastructure_compliance_table(elements, infrastructure_data)
            
            # If validation results are provided, add them to the report
            if validation_results is not None and not validation_results.empty:
                elements.append(Spacer(1, 12))
                create_classroom_validation_table(elements, validation_results)

            validation_summary = ""
            if validation_results is not None and not validation_results.empty:
                validation_summary = "Classroom Validation Details:\n"
                for _, row in validation_results.iterrows():
                    validation_summary += f"- Room Type: {row['Room Type (3rd Column)']}, Capacity: {row['Capacity (4th Column)']} - Status: {row['Status']}\n"
            # # Build the PDF
            # doc.build(elements)

            # nlp = spacy.load("en_core_web_sm")

            # # Extract text from the PDF
            # output_pdf.seek(0)
            # pdf_text = PyPDF2.PdfFileReader(output_pdf).getPage(0).extractText()

            # # Process the text using Spacy
            # doc = nlp(pdf_text)

            # # Extract relevant information from the text
            # extracted_info = ""
            # for ent in doc.ents:
            #     extracted_info += f"{ent.text} ({ent.label_})\n"



            # Use the Gemini API to generate a report
            genai.configure(api_key="Google studio API")
            # model = genai.GenerativeModel("gemini-1.5-flash")
            model = genai.GenerativeModel(
                "gemini-2.5-flash"
            )
            prompt = f"""
                You are an expert educational compliance inspector reviewing an AICTE compliance report.

                Compliance Overview:
                - Total Professors: {faculty_data['professors']} (Required: {faculty_data['required_professors']})
                - Total Associate Professors: {faculty_data['associate_professors']} (Required: {faculty_data['required_associate_professors']})
                - Total Assistant Professors: {faculty_data['assistant_professors']} (Required: {faculty_data['required_assistant_professors']})
                
                Infrastructure Details:
                - Classrooms: {infrastructure_data['classrooms']} (Required: {infrastructure_data['required_classrooms']})
                - Laboratories: {infrastructure_data['labs']} (Required: {infrastructure_data['required_labs']})
                - Workshops: {infrastructure_data['workshops']} (Required: {infrastructure_data['required_workshops']})
                - Smart Classrooms: {infrastructure_data['smart_classrooms']} (Required: {infrastructure_data['required_smart_classrooms']})

                Add a heading 'Actionable Insights:' before giving response.
                Analyze the compliance data and provide a comprehensive summary focusing on:
                1. Detailed breakdown of compliance status
                2. Specific areas of non-compliance
                3. Constructive suggestions for improvement
                4. Potential risks or challenges in meeting AICTE norms

                Classroom Space Validation:
                {validation_summary}

                For each non-compliant area, provide:
                - Current status
                - Specific shortfall
                - Concrete recommendations for improvement
                - Potential impact on educational quality
                Format your response as a professional, actionable report.
                """
            try:
                response = model.generate_content(prompt)
                ai_summary = response.text
            except Exception as e:
                print(f"Gemini API error: {e}")
                ai_summary = "Unable to generate AI-powered insights"

            
            print("🔥 USING NEW CODE")

            summary_title = Paragraph("<b>AI-Generated Compliance Insights</b>", styles['Heading2'])
            elements.append(summary_title)
            
            # Add the AI summary as a paragraph
            summary_elements = markdown_to_formatted_paragraphs(ai_summary, styles)
            elements.extend(summary_elements)
            doc.build(elements)

            output_pdf.seek(0)
            final_pdf_content = output_pdf.read()
            # Save the generated report in the database
            compliance_report = compliancereport(
                # college_name=info.college_name,
                college_name=info.college_id,
                intake=info.intake,
                report_file=final_pdf_content
            )
            print("📄 Saving report to MongoDB...")
            compliance_report.save()


            return {"message": "Report generated and saved successfully", "report_id": str(compliance_report.id)}
        except Exception as e:
            # Log or re-raise with additional context
            raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


    total_professors, total_associate_professors, total_assistant_professors = analyze_faculty_data(excel_file)

    # Perform classroom and related data analysis
    total_labs, total_classrooms, total_dept_library,workshops, smart_classroom = analyze_classroom_data(excel_file)

    # Classroom validation
    validation_results = validate_classroom_details(excel_file)

    # Get student intake from user
    student_intake = int(info.intake)
    print(student_intake)
    # Prepare faculty data for report
    faculty_data = {
        'professors': total_professors,
        'required_professors': student_intake / 180,
        'professor_compliance': 'Compliant' if total_professors >= student_intake / 180 else 'Non-Compliant',
        'associate_professors': total_associate_professors,
        'required_associate_professors': student_intake / 90,
        'associate_professor_compliance': 'Compliant' if total_associate_professors >= student_intake / 90 else 'Non-Compliant',
        'assistant_professors': total_assistant_professors,
        'required_assistant_professors': student_intake / 30,
        'assistant_professor_compliance': 'Compliant' if total_assistant_professors >= student_intake / 30 else 'Non-Compliant',
    }

    # Prepare infrastructure data for report
    D = student_intake / 60
    dept = 1  # Assuming one department, adjust as needed
    labs = 2 * dept * 3  # Calculate required labs based on intake

    infrastructure_data = {
        'classrooms': total_classrooms,
        'required_classrooms': D,
        'classroom_compliance': 'Compliant' if total_classrooms >= D else 'Non-Compliant',
        'labs': total_labs,
        'required_labs': labs,
        'lab_compliance': 'Compliant' if total_labs >= labs else 'Non-Compliant',
        'workshops': workshops,
        'required_workshops': 1,
        'workshop_compliance': 'Compliant' if workshops >= 1 else 'Non-Compliant',
        'smart_classrooms': smart_classroom,
        'required_smart_classrooms': 4,
        'smart_classroom_compliance': 'Compliant' if smart_classroom >= 4 else 'Non-Compliant',
    }

    # Generate the report with validation results
    report_result = generate_report(
        faculty_data, 
        infrastructure_data, 
        validation_results, 
        # college_name=info.college_name,
        college_name=info.college_id,
        intake=info.intake
    )

    return report_result


# ===================== NEW DEFICIENCY API =====================

@app.post("/generate-deficiency-report/")
async def generate_deficiency_report(info: CollegeLoginInfo):
    try:
        print("🚨 Generating deficiency report for:", info.college_id)

        compliance = compliancereport.objects(
            college_name=info.college_id
        ).first()

        if not compliance:
            raise HTTPException(status_code=404, detail="Compliance report not found")

        # 📄 Imports
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer,
            ListFlowable, ListItem, HRFlowable
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib import colors
        from io import BytesIO

        # 📄 Setup PDF
        output_pdf = BytesIO()
        doc = SimpleDocTemplate(
            output_pdf,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()

        # 🎨 Custom Styles
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Title'],
            alignment=TA_CENTER,
            fontSize=18,
            spaceAfter=10
        )

        section_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=colors.darkblue,
            spaceAfter=6
        )

        normal_style = ParagraphStyle(
            'NormalStyle',
            parent=styles['Normal'],
            fontSize=11,
            leading=15
        )

        # 🧾 Content
        elements = []

        # Title
        elements.append(Paragraph("Deficiency Report", title_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
        elements.append(Spacer(1, 15))

        # College Info
        elements.append(Paragraph(f"<b>College ID:</b> {info.college_id}", normal_style))
        elements.append(Spacer(1, 12))

        # Observations Section
        elements.append(Paragraph("Observations", section_style))

        observations = [
            "Some infrastructure is below AICTE norms",
            "Faculty count may be insufficient",
            "Labs and classrooms need improvement"
        ]

        obs_list = ListFlowable(
            [ListItem(Paragraph(item, normal_style)) for item in observations],
            bulletType='bullet',
            leftIndent=20
        )

        elements.append(obs_list)
        elements.append(Spacer(1, 15))

        # Recommendations Section
        elements.append(Paragraph("Recommendations", section_style))

        recommendations = [
            "Improve infrastructure facilities",
            "Hire more qualified faculty",
            "Upgrade labs and classrooms"
        ]

        rec_list = ListFlowable(
            [ListItem(Paragraph(item, normal_style)) for item in recommendations],
            bulletType='bullet',
            leftIndent=20
        )

        elements.append(rec_list)
        elements.append(Spacer(1, 20))

        # Footer note
        elements.append(Paragraph(
            "<i>This report is automatically generated based on AICTE compliance analysis.</i>",
            styles['Italic']
        ))

        # 🏗 Build PDF
        doc.build(elements)
        output_pdf.seek(0)

        # 💾 Save to MongoDB
        DeficiencyReport(
            college=info.college_id,
            branch="ALL",
            file=output_pdf.read()
        ).save()

        print("✅ Deficiency report saved")

        return {"message": "Deficiency report generated successfully"}

    except Exception as e:
        print("❌ ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))
    


    
    # ===================== /generate-pattern-report =====================

@app.post("/generate-pattern-report/")
async def generate_pattern_report(data: dict):
    try:
        import os
        import re
        from io import BytesIO
        import pdfplumber

        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer,
            ListFlowable, ListItem, HRFlowable
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib import colors

        from google import genai

        # -------------------------
        # 🔹 INPUT VALIDATION
        # -------------------------
        filename = data.get("filename")
        if not filename:
            return {"error": "Filename is required"}

        file_path = os.path.join("media", "docs", filename)


        if not os.path.exists(file_path):
            return {"error": "File not found"}

        print("📄 Generating pattern report for:", filename)



        

        # -------------------------
        # 📖 STEP 1: EXTRACT TEXT (BETTER)
        # -------------------------
        # text = ""

        # with pdfplumber.open(file_path) as pdf:
        #     for page in pdf.pages:
        #         page_text = page.extract_text()
        #         if page_text:
        #             text += page_text + "\n"


        text_data = []

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()

                for table in tables:
                    for row in table:
                        cleaned_row = []
                        for cell in row:
                            if cell:
                                cleaned_row.append(str(cell).strip())

                        if cleaned_row:
                            text_data.append(" | ".join(cleaned_row))

        # Convert to text
        text = "\n".join(text_data)


        # -------------------------
        # 🧹 STEP 2: CLEAN TEXT
        # -------------------------
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s+', ' ', text)

        # -------------------------
        # 🎯 STEP 3: FILTER RELEVANT CONTENT
        # -------------------------
        filtered_lines = []

        for line in text.split("\n"):
            if any(word in line.lower() for word in [
                "placement", "salary", "company", "%",
                "ctc", "package", "recruiter"
            ]):
                filtered_lines.append(line)

        text = "\n".join(filtered_lines)

        print("========== RAW TEXT SENT TO AI ==========")
        print(text[:1000])
        print("=========================================")


        # -------------------------
        # ⚠️ STEP 4: LIMIT INPUT SIZE
        # -------------------------
        text = text[:4000]

        print("🔍 FINAL TEXT SENT TO AI:\n", text[:500])

        # -------------------------
        # 🧠 STEP 5: RULE-BASED INSIGHTS
        # -------------------------
        insights = []

        if "placement" in text.lower():
            insights.append("Placement-related data is present")

        if "%" in text:
            insights.append("Placement percentage data detected")

        if "company" in text.lower():
            insights.append("Company participation mentioned")

        if "salary" in text.lower() or "package" in text.lower():
            insights.append("Salary/package trends available")

        if not insights:
            insights.append("Limited structured placement data found")

        # -------------------------
        # 🤖 STEP 6: AI INSIGHTS (STRONG PROMPT)
        # -------------------------
        client = genai.Client(api_key="Google studio API")

        try:
            prompt = f"""
You are a STRICT placement data analyst.

Analyze the given placement report content and generate SPECIFIC insights.

Rules:
- DO NOT give generic answers
- DO NOT repeat points
- Use only the given data
- Be concise and factual

FORMAT EXACTLY:

## Key Observations
- ...

## Strengths
- ...

## Weaknesses
- ...

## Suggestions
- ...

CONTENT:
{text}
"""

            response = client.models.generate_content(
                model="models/gemini-2.5-flash",
                contents=prompt
            )

            ai_summary = response.text

        except Exception as e:
            print("❌ Gemini Error:", e)
            ai_summary = "AI insights could not be generated"

        # -------------------------
        # 📄 STEP 7: CREATE PDF
        # -------------------------
        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Title'],
            alignment=TA_CENTER,
            fontSize=18,
            spaceAfter=12
        )

        section_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Heading2'],
            textColor=colors.darkblue,
            spaceAfter=8
        )

        normal_style = ParagraphStyle(
            'NormalStyle',
            parent=styles['Normal'],
            leading=14,
            spaceAfter=6
        )

        elements = []

        # Header
        elements.append(Paragraph("Pattern Analysis Report", title_style))
        elements.append(HRFlowable(width="100%", thickness=1))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(f"<b>Analyzed File:</b> {filename}", normal_style))
        elements.append(Spacer(1, 10))

        # Rule-based insights
        elements.append(Paragraph("Key Observations", section_style))
        elements.append(ListFlowable(
            [ListItem(Paragraph(i, normal_style)) for i in insights]
        ))
        elements.append(Spacer(1, 15))

        # AI Insights
        elements.append(Paragraph("AI-Generated Insights", section_style))
        elements.append(Spacer(1, 10))

        ai_summary = ai_summary.replace("**", "").replace("*", "")

        bullets = []

        for line in ai_summary.split("\n"):
            line = line.strip()

            if not line:
                continue

            if line.startswith("##"):
                if bullets:
                    elements.append(ListFlowable(bullets))
                    bullets = []

                elements.append(Spacer(1, 10))
                elements.append(Paragraph(line.replace("##", ""), section_style))

            elif line.startswith("-"):
                bullets.append(ListItem(Paragraph(line[1:].strip(), normal_style)))

            else:
                if bullets:
                    elements.append(ListFlowable(bullets))
                    bullets = []

                elements.append(Paragraph(line, normal_style))

        if bullets:
            elements.append(ListFlowable(bullets))

        elements.append(Spacer(1, 20))

        elements.append(HRFlowable(width="100%", thickness=0.5))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(
            "<i>This report is generated using AI-based document analysis.</i>",
            styles['Italic']
        ))

        doc.build(elements)

        # -------------------------
        # 💾 STEP 8: SAVE TO MONGO
        # -------------------------
        buffer.seek(0)
        pdf_data = buffer.read()

        pattern_report = PatternReport(filename=filename)

        print("📄 Saving to MongoDB...")
        pattern_report.file.put(pdf_data, content_type='application/pdf')
        pattern_report.save()

        print("✅ Saved:", pattern_report.id)

        return {
            "message": "Pattern report generated successfully",
            "report_id": str(pattern_report.id)
        }

    except Exception as e:
        print("❌ ERROR:", e)
        return {"error": str(e)}
    
    
 