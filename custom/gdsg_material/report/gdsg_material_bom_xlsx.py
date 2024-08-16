import base64
import io
from odoo import models
from datetime import date, datetime, time
import logging

_logger = logging.getLogger('gdsg_material_bom_xlsx')

class Gdsg_material_bom_xlsx(models.AbstractModel):
    _name = "report.gdsg_material.bom.report_material_xlsx"
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Gdsg Material Bom Xlsx'

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

            sheet = workbook.add_worksheet('Bom')
            sheet.set_column('A:A', 10)
            sheet.set_column('B:B', 15)
            sheet.set_column('C:C', 30)
            sheet.set_column('D:D', 25)
            sheet.set_column('E:E', 15)
            sheet.set_column('F:F', 15)
            sheet.set_column('G:G', 15)
            sheet.set_column('H:H', 15)
            sheet.set_column('I:I', 30)
            self_data_id = data['form_data']['id']
            bom_data = self.env['gdsg_material.bom'].sudo().browse(int(self_data_id))
            #header
            company_name = self.env.company.name
            company_vat = self.env.company.vat
            sheet.write(0, 0, company_name, bold)
            if company_vat:
                sheet.write(1, 0, 'VAT: %s' % company_vat, bold)
            line_num = 3
            sheet.merge_range(line_num, 0, line_num, 8, '', merge_format)
            sheet.write(line_num, 0, 'DANH SÁCH NGUYÊN VẬT LIỆU - LỚP %s' % bom_data.class_num, header)
            line_num += 1
            sheet.merge_range(line_num, 0, line_num, 8, '', merge_format)
            sheet.write(line_num, 0, 'CHỦ ĐỀ: %s' % bom_data.topic_id.name, header)
            line_num += 1
            sheet.merge_range(line_num, 0, line_num, 8, '', merge_format)
            sheet.write(line_num, 0, 'THỜI LƯỢNG: %s tiết' % bom_data.time, header1)
            line_num += 1
            sheet.merge_range(line_num, 0, line_num, 8, '', merge_format)
            sheet.write(line_num, 0, 'HS/Nhóm: %s' % bom_data.group_student, header1)
            line_num += 2
            sheet.merge_range(line_num, 0, line_num + 1, 0, '', merge_format)
            sheet.write(line_num, 0, 'STT', line_header)
            sheet.merge_range(line_num, 1, line_num + 1, 1, '', merge_format)
            sheet.write(line_num, 1, 'Mã VT', line_header)
            sheet.merge_range(line_num, 2, line_num + 1, 2, '', merge_format)
            sheet.write(line_num, 2, 'Tên nguyên liệu', line_header)
            sheet.merge_range(line_num, 3, line_num + 1, 3, '', merge_format)
            sheet.write(line_num, 3, 'Yêu cầu', line_header)
            sheet.merge_range(line_num, 4, line_num + 1, 4, '', merge_format)
            sheet.write(line_num, 4, 'Đơn vị', line_header)
            sheet.merge_range(line_num, 5, line_num, 7, '', merge_format)
            sheet.write(line_num, 5, 'Số lượng trên', line_header)
            sheet.write(line_num, 6, '', line_header)
            sheet.write(line_num, 7, '', line_header)
            sheet.merge_range(line_num, 8, line_num + 1, 8, '', merge_format)
            sheet.write(line_num, 8, 'Ghi chú', line_header)
            line_num += 1
            sheet.write(line_num, 0, '', border_format)
            sheet.write(line_num, 1, '', border_format)
            sheet.write(line_num, 2, '', border_format)
            sheet.write(line_num, 3, '', border_format)
            sheet.write(line_num, 4, '', border_format)
            sheet.write(line_num, 5, 'Nhóm', line_header)
            sheet.write(line_num, 6, 'Lớp', line_header)
            sheet.write(line_num, 7, 'Khối', line_header)
            sheet.write(line_num, 8, '', border_format)
            line_num += 1
            #details
            stt = 1
            for line in bom_data.line_ids:
                sheet.write(line_num, 0, stt, line_text_center)
                sheet.write(line_num, 1, line.product_id.default_code if line.product_id.default_code else '', line_text_format)
                sheet.write(line_num, 2, line.product_id.name if line.product_id.name else '', line_text_format)
                sheet.write(line_num, 3, line.require if line.require else '', line_text_format)
                sheet.write(line_num, 4, line.uom_id.name if line.uom_id.name else '', line_text_center)
                sheet.write(line_num, 5, line.quantity if line.use_for == 'group' else '', line_int_number_format_center)
                sheet.write(line_num, 6, line.quantity if line.use_for == 'class' else '', line_int_number_format_center)
                sheet.write(line_num, 7, line.quantity if line.use_for == 'teacher' else '', line_int_number_format_center)
                sheet.write(line_num, 8, line.note if line.note else '', line_text_format)
                stt += 1
                line_num += 1

            #footer
            line_num += 1
            sheet.merge_range(line_num, 0, line_num, 8, '', merge_format)
            sheet.write(line_num, 0, 'TP.Hồ Chí Minh, ngày %s tháng %s năm %s' % (datetime.strftime(datetime.utcnow(), '%d')
                                                                           , datetime.strftime(datetime.utcnow(), '%m')
                                                                           , datetime.strftime(datetime.utcnow(), '%Y')), footer_date)
            line_num += 1
            sheet.merge_range(line_num, 0, line_num, 2, '', merge_format)
            sheet.write(line_num, 0, 'Giám đốc duyệt', signment)
            sheet.merge_range(line_num, 3, line_num, 4, '', merge_format)
            sheet.write(line_num, 3, 'Phòng đào tạo', signment)
            sheet.merge_range(line_num, 5, line_num, 6, '', merge_format)
            sheet.write(line_num, 5, 'Kiểm soát', signment)
            sheet.merge_range(line_num, 7, line_num, 8, '', merge_format)
            sheet.write(line_num, 7, 'Người lập', signment)
        except Exception as e:
            _logger.error('generate_xlsx_report exception: %s' % e)

