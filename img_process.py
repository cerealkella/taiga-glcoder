from os import path, remove
from PIL import Image, ImageFont, ImageDraw
import time
import tempfile
import PyPDF2
import datetime
from reportlab.pdfgen import canvas


def _get_tmp_filename(suffix=".pdf"):
    with tempfile.NamedTemporaryFile(suffix=".pdf") as fh:
        return fh.name


def _get_output_filename(input_file):
    output_filename = "{}_signed{}".format(
            *path.splitext(input_file)
        )
    return output_filename


def sign_pdf(pdf, signature, text, coords, sigdate=False):
    # for y coord, pass in pixels from top of page, as the logic
    # of c.drawImage measures from the bottom to the top. I don't know why
    page_num, x1, y, width, height = [int(a) for a in coords.split("x")]
    page_num -= 1

    output_filename = _get_output_filename(pdf)

    pdf_fh = open(pdf, 'rb')
    sig_tmp_fh = None

    pdf = PyPDF2.PdfFileReader(pdf_fh)
    # Set y1 to pixels from top of page
    y1 = pdf.getPage(page_num).mediaBox[3] - y
    print(pdf.getPage(page_num).mediaBox)
    print(y1)
    writer = PyPDF2.PdfFileWriter()
    sig_tmp_filename = None

    for i in range(0, pdf.getNumPages()):
        page = pdf.getPage(i)

        if i == page_num:
            # Create PDF for signature
            sig_tmp_filename = _get_tmp_filename()
            c = canvas.Canvas(sig_tmp_filename, pagesize=page.cropBox)
            c.drawImage(signature, x1, y1, width, height, mask='auto')
            if text != "" and text is not None:
                c.drawString(x1, y1, text)  # text above signature
            if sigdate:
                c.drawString(x1, y1 - 32,
                             datetime.datetime.now().strftime("%Y-%m-%d"))
            c.showPage()
            c.save()

            # Merge PDF in to original page
            sig_tmp_fh = open(sig_tmp_filename, 'rb')
            sig_tmp_pdf = PyPDF2.PdfFileReader(sig_tmp_fh)
            sig_page = sig_tmp_pdf.getPage(0)
            sig_page.mediaBox = page.mediaBox
            page.mergePage(sig_page)

        writer.addPage(page)

    with open(output_filename, 'wb') as fh:
        writer.write(fh)

    for handle in [pdf_fh, sig_tmp_fh]:
        if handle:
            handle.close()
    if sig_tmp_filename:
        remove(sig_tmp_filename)
    return output_filename


def sign_image(img_file, signature, text):
    img = Image.open(img_file)
    draw = ImageDraw.Draw(img)
    glfont = ImageFont.truetype("fonts/Roboto-Black.ttf", 16)
    sigfont = ImageFont.truetype("fonts/HoneyScript-SemiBold.ttf", 40)
    draw.text((200, 10), signature, (0, 0, 0), font=sigfont)
    draw.text((200, 50), text, (0, 0, 200), font=glfont)
    output_filename = _get_output_filename(img_file)
    img.save(output_filename)
    return output_filename


def _create_sig(signature):
    img = Image.new('RGBA', (735, 150))
    draw = ImageDraw.Draw(img)
    sigfont = ImageFont.truetype("fonts/HoneyScript-SemiBold.ttf", 70)
    draw.text((20, 30), signature, (0, 0, 200), font=sigfont)
    outputfile = "signature.png"
    img.save(outputfile, 'PNG')
    return outputfile


def sign_invoice(input_file, sig_name, text):
    filename, file_extension = path.splitext(input_file)
    if file_extension.lower() == ".pdf":
        sigfile = _create_sig(sig_name)
        signed_file = sign_pdf(input_file, sigfile, text, "1x125x40x150x40")
        # signed_file = sign_pdf(input_file, sigfile, text, "1x125x735x150x40")
    else:
        signed_file = sign_image(input_file, sig_name, text)
    return signed_file


# print(sign_invoice("tester.pdf", "Justin", "4144144 - $33.44"))
# _create_sig("Mr. Test Van Testerson")
