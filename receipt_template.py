import base64
from datetime import datetime
import os

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    return ""

def generate_receipt_html(saved_data):
    left_logo_b64 = get_base64_image(os.path.join("src", "left_logo.jpg"))
    right_logo_b64 = get_base64_image(os.path.join("src", "right_logo.png"))

    left_img_tag = (
        f'<img src="data:image/jpeg;base64,{left_logo_b64}" style="width:40px; height:40px; object-fit:contain;" />'
        if left_logo_b64
        else "<b>MP GOV</b>"
    )
    right_img_tag = (
        f'<img src="data:image/png;base64,{right_logo_b64}" style="width:80px; height:auto; object-fit:contain;" />'
        if right_logo_b64
        else "<b>NIC</b>"
    )

    current_time = datetime.now().strftime("%d/%m/%Y %H:%M")

    single_receipt_markup = f"""
    <table class="receipt-table">
        <tr>
            <td class="center" style="text-align: center; width: 16%;">
                {left_img_tag}
            </td>
            <td style="text-align: center; width: 64%;">
                <span style="font-size: 11pt;">कार्यालय कलेक्टर</span><br/>
                <span style="font-size: 12pt; font-weight: bold;">जन आवेदन</span><br/>
                <span style="font-size: 8.5pt;">आपकी शिकायत दर्ज कर ली गयी हैं जिसका विवरण नीचे दिया गया हैं</span>
            </td>
            <td class="center" style="text-align: center; width: 20%;">
                {right_img_tag}
            </td>
        </tr>
        <tr>
            <td style="font-weight: bold;">Receipt No.</td>
            <td>{saved_data['receipt_no']}</td>
            <td style="text-align: right;"><b>Date:</b> {saved_data['receipt_date']}</td>
        </tr>
        <tr>
            <td style="font-weight: bold;">Applicant Name</td>
            <td colspan="2">{saved_data['applicant_name']}</td>
        </tr>
        <tr>
            <td style="font-weight: bold;">Applicant Address</td>
            <td colspan="2">{saved_data['applicant_address']}</td>
        </tr>
        <tr>
            <td style="font-weight: bold;">Subject</td>
            <td colspan="2">{saved_data['subject']}</td>
        </tr>
        <tr>
            <td style="font-weight: bold;">Marked Office</td>
            <td colspan="2">{saved_data['marked_office']}</td>
        </tr>
        <tr>
            <td style="font-weight: bold;">Details</td>
            <td colspan="2">{saved_data['details']}</td>
        </tr>
    </table>
    <div style="font-size: 9pt; margin-top: 3px; text-align: right;">
        <span>Print Date: {current_time}</span>
    </div>
    """

    component_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #f4f6f9; margin: 0; padding: 10px; display: flex; justify-content: center; align-items: flex-start; }}
        .receipt-container {{ width: 100%; max-width: 650px; background: white; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .receipt-section {{ height: 48%; }}
        .cut-line {{ border-top: 2px dashed #666; margin: 75px 0; text-align: center; position: relative; }}
        .cut-line span {{ background: white; padding: 0 10px; font-size: 9pt; color: #666; position: relative; top: -10px; }}
        .receipt-table {{ width: 100%; border-collapse: collapse; border: 1.5px solid black; }}
        .receipt-table th, .receipt-table td {{ border: 1px solid black; padding: 5px 8px; font-size: 9.5pt; vertical-align: middle; color: black; text-align: left; }}
        .center {{ text-align: center; }}
        .print-btn-container {{ text-align: center; margin-top: 15px; }}
        .print-btn {{ background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; font-size: 14px; font-weight: bold; cursor: pointer; }}
        .print-btn:hover {{ background-color: #0056b3; }}
        @media print {{
            body {{ background: white; display: block; }}
            .print-btn-container {{ display: none; }}
            .receipt-container {{ box-shadow: none; width: 100%; margin: 0; padding: 0; }}
            @page {{ size: A4 portrait; margin: 10mm; }}
        }}
    </style>
    </head>
    <body>
    <div class="receipt-container">
        <div class="receipt-section">{single_receipt_markup}</div>
        <div class="cut-line"><span></span></div>
        <div class="receipt-section">{single_receipt_markup}</div>
        <div class="print-btn-container">
            <button class="print-btn" onclick="window.print()">🖨️ Print / Save 2-Copy A4 Portrait PDF</button>
        </div>
    </div>
    </body>
    </html>
    """
    return component_html