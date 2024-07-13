import base64
import io
from odoo import models
from datetime import date, datetime, time
import logging

_logger = logging.getLogger('gdsg_refund_core_xlsx')

class Gdsg_refund_core_xlsx(models.AbstractModel):
    _name = "report.gdsg_refund.core.report_refund_xlsx"
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Gdsg Refund Core Xlsx'

    def generate_xlsx_report(self, workbook, data, refunds):
        try:
            #define format
            header = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center'})
            header1 = workbook.add_format({'bold': True, 'font_size': 12, 'align': 'center'})
            bold = workbook.add_format({'bold': True})
            format_label = workbook.add_format({'font_size': 12, 'valign': 'top', 'bold': False, 'left': True, 'right': True, 'text_wrap': True})
            merge_format = workbook.add_format({'align': 'center'})
            footer_date = workbook.add_format({'italic': True, 'font_size': 12, 'align': 'right'})
            signment = workbook.add_format({'bold': True, 'font_size': 12, 'align': 'center'})
            number = workbook.add_format({'num_format': '#,##0', 'border': 1})
            line_border = workbook.add_format({'border': 1})
            line_header = workbook.add_format({'border': 1, 'bold': True})

            sheet = workbook.add_worksheet('Refund')
            sheet.set_column('A:A', 30)
            sheet.set_column('B:B', 15)
            sheet.set_column('C:C', 15)
            self_data_id = data['form_data']['id']
            refund_data = self.env['gdsg_refund.core'].sudo().browse(int(self_data_id))
            #header
            company_name = self.env.company.name
            company_vat = self.env.company.vat
            sheet.write(0, 0, company_name, bold)
            if company_vat:
                sheet.write(1, 0, company_vat, bold)
            sheet.merge_range(3, 0, 3, 2, '', merge_format)
            sheet.write(3, 0, 'TIỀN HOÀN TRẢ LẠI TRƯỜNG', header)
            sheet.merge_range(4, 0, 4, 2, '', merge_format)
            sheet.write(4, 0, 'Tháng hoàn tiền: %s' % refund_data.refund_period, header1)
            sheet.merge_range(5, 0, 5, 2, '', merge_format)
            sheet.write(5, 0, refund_data.partner_id.name, header1)
            sheet.write(7, 0, 'Khoản mục', line_header)
            sheet.write(7, 1, 'Giá trị', line_header)
            sheet.write(7, 2, 'Ghi chú', line_header)

            row = 8
            #details
            for line in refund_data.refund_line:
                sheet.write(row, 0, line.rule_id.name, line_border)
                sheet.write(row, 1, line.amount, number)
                if line.note:
                    sheet.write(row, 2, line.note, line_border)
                else:
                    sheet.write(row, 2, '', line_border)
                row += 1


            #footer
            row += 1
            sheet.merge_range(row, 0, row, 2, '', merge_format)
            sheet.write(row, 0, 'TP.Hồ Chí Minh, ngày %s tháng %s năm %s' % (datetime.strftime(datetime.utcnow(), '%d')
                                                                           , datetime.strftime(datetime.utcnow(), '%m')
                                                                           , datetime.strftime(datetime.utcnow(), '%Y')), footer_date)
            row += 1
            sheet.write(row, 0, 'Xác nhận của công ty', signment)
            sheet.merge_range(row, 1, row, 2, '', merge_format)
            sheet.write(row, 1, 'Xác nhận của nhà trường', signment)
        except Exception as e:
            _logger.error('generate_xlsx_report exception: %s' % e)

