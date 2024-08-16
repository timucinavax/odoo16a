import base64
import io
from odoo import models
from datetime import date, datetime, time
import logging

_logger = logging.getLogger('gdsg_material_bom_xlsx')

class Gdsg_material_purchase_request_xlsx(models.AbstractModel):
    _name = "report.gdsg_material.report_purchase_request_xlsx"
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Gdsg Material Purchase Request Xlsx'

    def generate_xlsx_report(self, workbook, data, refunds):
        try:
            #define format
            header = workbook.add_format({'font_name': 'Times New Roman', 'bold': True, 'font_size': 16, 'align': 'center'})
            header1 = workbook.add_format({'font_name': 'Times New Roman', 'font_size': 12, 'align': 'center'})
            bold = workbook.add_format({'font_name': 'Times New Roman', 'bold': True})
            format_label = workbook.add_format({'font_name': 'Times New Roman', 'font_size': 12, 'valign': 'top', 'bold': False, 'left': True, 'right': True, 'text_wrap': True})
            merge_format = workbook.add_format({'font_name': 'Times New Roman', 'align': 'center', 'valign': 'vcenter'})
            footer_date = workbook.add_format({'font_name': 'Times New Roman', 'italic': True, 'font_size': 12, 'align': 'right'})
            signment = workbook.add_format({'font_name': 'Times New Roman', 'bold': True, 'font_size': 12, 'align': 'center'})
            line_number_format = workbook.add_format({'font_name': 'Times New Roman', 'num_format': '#,##0', 'border': 1})
            line_number_format_center = workbook.add_format({'font_name': 'Times New Roman', 'num_format': '#,##0', 'border': 1, 'align': 'center'})
            line_int_number_format_center = workbook.add_format({'font_name': 'Times New Roman', 'num_format': '#,##0', 'border': 1, 'align': 'center'})
            line_header = workbook.add_format({'font_name': 'Times New Roman', 'border': 1, 'bold': True, 'align': 'center', 'valign': 'vcenter'})
            border_format = workbook.add_format({'font_name': 'Times New Roman', 'border': 1})
            line_text_format = workbook.add_format({'font_name': 'Times New Roman', 'border': 1})
            line_text_center = workbook.add_format({'font_name': 'Times New Roman', 'border': 1, 'align': 'center'})

            sheet = workbook.add_worksheet('Purchase Request')
            sheet.set_column('A:A', 10)
            sheet.set_column('B:B', 15)
            sheet.set_column('C:C', 30)
            sheet.set_column('D:D', 30)
            sheet.set_column('E:E', 15)
            sheet.set_column('F:F', 15)
            sheet.set_column('G:G', 30)
            self_data_id = data['form_data']['id']
            header_data = self.env['gdsg_material.purchase.request'].sudo().browse(int(self_data_id))
            #header
            company_name = self.env.company.name
            company_vat = self.env.company.vat
            sheet.write(0, 0, company_name, bold)
            if company_vat:
                sheet.write(1, 0, 'VAT: %s' % company_vat, bold)
            line_num = 3
            sheet.merge_range(line_num, 0, line_num, 8, '', merge_format)
            sheet.write(line_num, 0, 'PHIẾU ĐỀ NGHỊ MUA VẬT TƯ', header)
            line_num += 2
            sheet.write(line_num, 0, 'STT', line_header)
            sheet.write(line_num, 1, 'Mã VT', line_header)
            sheet.write(line_num, 2, 'Tên VT', line_header)
            sheet.write(line_num, 3, 'Quy cách', line_header)
            sheet.write(line_num, 4, 'ĐVT', line_header)
            sheet.write(line_num, 5, 'Cần mua', line_header)
            sheet.write(line_num, 6, 'Ghi chú', line_header)
            line_num += 1
            #details
            stt = 1
            for line in header_data.line_ids:
                if line.convert_request_purchase:
                    if line.convert_request_purchase > 0:
                        sheet.write(line_num, 0, stt, line_text_center)
                        sheet.write(line_num, 1, line.product_id.default_code if line.product_id.default_code else '', line_text_format)
                        sheet.write(line_num, 2, line.product_id.name if line.product_id.name else '', line_text_format)
                        sheet.write(line_num, 3, line.product_id.description if line.product_id.description else '', line_text_format)
                        sheet.write(line_num, 4, line.product_id.purchase_uom_id.name if line.product_id.purchase_uom_id.name else '', line_text_center)
                        sheet.write(line_num, 5, line.convert_request_purchase if line.convert_request_purchase else '', line_int_number_format_center)
                        sheet.write(line_num, 6, line.note if line.note else '', line_text_format)
                        stt += 1
                        line_num += 1

            #footer
            line_num += 1
            sheet.merge_range(line_num, 0, line_num, 6, '', merge_format)
            sheet.write(line_num, 0, 'TP.Hồ Chí Minh, ngày %s tháng %s năm %s' % (datetime.strftime(datetime.utcnow(), '%d')
                                                                           , datetime.strftime(datetime.utcnow(), '%m')
                                                                           , datetime.strftime(datetime.utcnow(), '%Y')), footer_date)
            line_num += 1
            sheet.merge_range(line_num, 0, line_num, 2, '', merge_format)
            sheet.write(line_num, 0, 'Giám đốc duyệt', signment)
            sheet.merge_range(line_num, 3, line_num, 5, '', merge_format)
            sheet.write(line_num, 3, 'Trưởng bộ phận', signment)
            sheet.write(line_num, 6, 'Người đề nghị', signment)
        except Exception as e:
            _logger.error('generate_xlsx_report exception: %s' % e)

