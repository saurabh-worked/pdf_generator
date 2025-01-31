# creator/views.py
import subprocess
import tempfile
import os
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
import json
import time


# @login_required
@csrf_exempt
def post_pdf(request):
    try:
        # Custom header verification
        custom_header_value = request.headers.get('Custom-Header')
        if custom_header_value != '$2a$10$oJooI9PtFPl/Dv1zR.ULQe/HdP/hh9X8rlxF8vNhU5m5bM7InY61C':
            return JsonResponse({"error": "Unauthorized request"}, status=status.HTTP_403_FORBIDDEN)

        # Get the HTML content from the request
        html_content = json.loads(request.body.decode('utf-8'))

        if not html_content:
            return JsonResponse({"error": "HTML content is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate a unique timestamp-based filename for the PDF
        timestamp = int(time.time())  # Unix timestamp
        pdf_filename = f'proposal_{timestamp}.pdf'

        # Create a temporary HTML file to pass to the Python script
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as temp_html_file:
            temp_html_file.write(html_content)
            temp_html_file.close()  # Close the file before passing it to subprocess

            # The path where PDF will be temporarily saved
            output_pdf_path = os.path.join(tempfile.gettempdir(), pdf_filename)

            # Run the Python script using subprocess, passing the HTML file path and output PDF path
            result = subprocess.run(
                ['python', r'D:\proposalpdfgeneration\pdf.py', temp_html_file.name, output_pdf_path],
                text=True, capture_output=True
            )

        # Clean up the temporary HTML file
        os.remove(temp_html_file.name)

        # Check if the Python script executed successfully
        if result.returncode != 0:
            return JsonResponse({"error": f"Error generating PDF: {result.stderr}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Read the generated PDF file as binary data
        with open(output_pdf_path, 'rb') as pdf_file:
            pdf_data = pdf_file.read()

        # Clean up the temporary PDF file
        os.remove(output_pdf_path)

        # Return the PDF file as a response
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
        return response

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
