from fpdf import FPDF

def generate_report(num_videos:int, time_taken:int, exceptions:list[str], file_path:str):
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_font('Arial', 'B', 24)
    pdf.cell(40, 10, "Trending TikTok Videos Report\n\n")
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(40, 10, "A short report summarizing the actions performed.\n")
    pdf.cell(40, 10, f"Number of videos processed: \n`{num_videos}`\n")
    pdf.cell(40, 10, f"Time taken for the entire process: \n`{round(time_taken, 2)}` seconds\n")

    if exceptions:
        pdf.set_font('Arial', 'B', 18)
        pdf.cell(40, 10, "Exceptions:\n\n")
        pdf.set_font('Arial', 'B', 8)
        for idx, exc in enumerate(exceptions, 1):
            pdf.cell(40, 10, f"{idx}. {exc}\n")
        pdf.cell(40, 10, "\n")

    pdf.output(file_path)