from fpdf import FPDF

def generate_report(num_videos:int, time_taken:int, exceptions:list[str], file_path:str):
    w = 10
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_font('Arial', 'B', 24)
    pdf.cell(40, w, "Trending TikTok Videos Report\n\n")
    pdf.set_font('Arial', 'B', 12)
    w += 20
    pdf.cell(40, w, "A short report summarizing the actions performed.\n")
    w += 10
    pdf.cell(40, w, f"Number of videos processed: \n{num_videos}\n")
    w += 10
    pdf.cell(40, w, f"Time taken for the entire process: \n{round(time_taken, 2)} seconds\n")
    w += 10

    if exceptions:
        pdf.set_font('Arial', 'B', 18)
        pdf.cell(40, w, "Exceptions:\n\n")
        w += 20
        pdf.set_font('Arial', 'B', 8)
        for idx, exc in enumerate(exceptions, 1):
            w += 10
            pdf.cell(40, w, f"{idx}. {exc}\n")
        w += 30
        pdf.cell(40, w, "\n")

    pdf.output(file_path)