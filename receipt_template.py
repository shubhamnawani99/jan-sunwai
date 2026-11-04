import base64
from datetime import datetime
import os
from zoneinfo import ZoneInfo

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    return ""

def generate_receipt_html(saved_data):
    left_logo_b64 = get_base64_image(os.path.join("src", "left_logo.jpg"))
    right_logo_b64 = get_base64_image(os.path.join("src", "right_logo.png"))

    left_img_tag = (
        f'<img src="data:image/jpeg;base64,{left_logo_b64}" style="width:50px; height:50px; object-fit:contain;" />'
        if left_logo_b64
        else "<b>MP GOV</b>"
    )
    right_img_tag = (
        f'<img src="data:image/png;base64,{right_logo_b64}" style="width:100px; height:auto; object-fit:contain;" />'
        if right_logo_b64
        else "<b>NIC</b>"
    )

    # Use explicit Indian Standard Time (IST, UTC+5:30) for print time
    current_time = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d/%m/%Y %H:%M")

    single_receipt_markup = f"""
    <table class="receipt-table">
        <tr>
            <td class="center" style="text-align: center; width: 16%;">
                {left_img_tag}
            </td>
            <td style="text-align: center; width: 64%;">
                <span style="font-size: 13.8pt;">कार्यालय कलेक्टर</span><br/>
                <span style="font-size: 14.8pt; font-weight: bold;">जन आवेदन</span><br/>
                <span style="font-size: 10.5pt;">आपकी शिकायत दर्ज कर ली गयी हैं जिसका विवरण नीचे दिया गया हैं</span>
            </td>
            <td class="center" style="text-align: center; width: 24%;">
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
    <div style="font-size: 11pt; margin-top: 4px; text-align: right;">
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
        .receipt-container {{ width: 100%; max-width: 650px; background: white; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); box-sizing: border-box; margin: 0 auto; }}
        .receipt-section-1 {{ width: 100%; }}
        .receipt-section-2 {{ width: 100%; margin-top: 30px; }}
        .receipt-table {{ width: 100%; border-collapse: collapse; border: 1.5px solid black; }}
        .receipt-table th, .receipt-table td {{ border: 1.5px solid black; padding: 5.5px 8px; font-size: 11.6pt; vertical-align: middle; color: black; text-align: left; }}
        .center {{ text-align: center; }}
        .print-btn-container {{ text-align: center; margin-top: 25px; }}
        .print-btn {{ background-color: #007bff; color: white; padding: 13px 26px; border: none; border-radius: 4px; font-size: 16.5px; font-weight: bold; cursor: pointer; }}
        .print-btn:hover {{ background-color: #0056b3; }}
        @media print {{
            @page {{ size: A4 portrait; margin: 10mm; }}
            html, body {{ background: white; width: 100%; height: 100%; margin: 0; padding: 0; display: block; }}
            .print-btn-container {{ display: none; }}
            .receipt-container {{ box-shadow: none; width: 100%; max-width: none; height: 277mm; max-height: 277mm; margin: 0 auto; padding: 0; position: relative; box-sizing: border-box; overflow: hidden; }}
            .receipt-section-1 {{ position: absolute; top: 0; left: 0; width: 100%; }}
            .receipt-section-2 {{ position: absolute; top: calc(55%); left: 0; width: 100%; margin-top: 0; }}
        }}
    </style>
    </head>
    <body>
    <div class="receipt-container">
        <div class="receipt-section-1">{single_receipt_markup}</div>
        <div class="receipt-section-2">{single_receipt_markup}</div>
        <div class="print-btn-container">
            <button class="print-btn" onclick="window.print()">🖨️ Print / Save 2-Copy A4 Portrait PDF</button>
        </div>
    </div>
    </body>
    </html>
    """
    return component_html