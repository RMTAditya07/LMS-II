from flask import Blueprint, request, jsonify, render_template, send_file
from .services import export_csv_service, get_csv_service, generate_monthly_report

from . import reports_bp

@reports_bp.route('/export/csv', methods=['GET'])
def export_csv():
    """
    Unified route to export CSV for sections, books, or book requests.
    Use query parameter `type` to specify export type.
    """
    export_type = request.args.get('type')
    response, status_code = export_csv_service(export_type)
    return jsonify(response), status_code


@reports_bp.route('/get_csv/<task_id>', methods=['GET'])
def get_csv(task_id):
    """
    Route to fetch the exported CSV file by task ID.
    """
    response, status_code = get_csv_service(task_id)
    if status_code == 200:
        return send_file(response["filename"], as_attachment=True)
    return jsonify(response), status_code


@reports_bp.route('/monthly', methods=['GET'])
def send_monthly_report():
    """
    Generates and renders a monthly report.
    """
    report_data = generate_monthly_report()
    return render_template('report.html', sections=report_data["sections"], book_requests=report_data["book_requests"])
