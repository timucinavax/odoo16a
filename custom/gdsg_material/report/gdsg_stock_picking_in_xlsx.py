import base64
import io
from odoo import models
from datetime import date, datetime, time
import logging
from num2words import num2words
from string import capwords

_logger = logging.getLogger('gdsg_stock_picking_in_xlsx')

class Stock_picking_xlsx(models.AbstractModel):
    _name = "report.stock.picking.report_stock_picking_in_xlsx"
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Gdsg Stock Picking In Xlsx'

    def generate_xlsx_report(self, workbook, data, refunds):
        try:
            #define format
            header = workbook.add_format({'font_name': 'Times New Roman', 'bold': True, 'font_size': 16, 'align': 'center'})
            header1 = workbook.add_format({'font_name': 'Times New Roman', 'font_size': 13, 'align': 'center', 'italic': True})
            bold = workbook.add_format({'font_name': 'Times New Roman', 'bold': True, 'font_size': 13})
            bold_italic = workbook.add_format({'font_name': 'Times New Roman', 'bold': True, 'italic': True, 'font_size': 13})
            header_top = workbook.add_format({'font_name': 'Times New Roman', 'bold': True, 'italic': True, 'align': 'center', 'font_size': 13})
            format_label = workbook.add_format({'font_name': 'Times New Roman', 'font_size': 13, 'valign': 'top', 'bold': False, 'left': True, 'right': True, 'text_wrap': True})
            merge_format = workbook.add_format({'font_name': 'Times New Roman', 'align': 'center', 'valign': 'vcenter', 'font_size': 13})
            footer_date = workbook.add_format({'font_name': 'Times New Roman', 'italic': True, 'font_size': 13, 'align': 'right'})
            footer_text = workbook.add_format({'font_name': 'Times New Roman', 'font_size': 13, 'align': 'left'})
            header_text = workbook.add_format({'font_name': 'Times New Roman', 'font_size': 13, 'align': 'left'})
            signment = workbook.add_format({'font_name': 'Times New Roman', 'bold': True, 'font_size': 13, 'align': 'center'})
            signment_1 = workbook.add_format({'font_name': 'Times New Roman', 'italic': True, 'font_size': 13, 'align': 'center'})
            line_number_format = workbook.add_format({'font_name': 'Times New Roman', 'num_format': '#,##0', 'border': 1, 'align': 'right', 'font_size': 13})
            line_number_format_bold = workbook.add_format({'font_name': 'Times New Roman', 'num_format': '#,##0', 'border': 1, 'align': 'right', 'bold': True, 'font_size': 13})
            line_number_format_center = workbook.add_format({'font_name': 'Times New Roman', 'num_format': '#,##0', 'border': 1, 'align': 'center', 'font_size': 13})
            line_int_number_format_center = workbook.add_format({'font_name': 'Times New Roman', 'num_format': '#,##0', 'border': 1, 'align': 'center', 'font_size': 13})
            line_header = workbook.add_format({'font_name': 'Times New Roman', 'border': 1, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'font_size': 13})
            border_format = workbook.add_format({'font_name': 'Times New Roman', 'border': 1, 'font_size': 13})
            line_text_format = workbook.add_format({'font_name': 'Times New Roman', 'border': 1, 'font_size': 13, 'text_wrap': True})
            line_text_center = workbook.add_format({'font_name': 'Times New Roman', 'border': 1, 'align': 'center', 'font_size': 13, 'text_wrap': True})

            sheet = workbook.add_worksheet('Phiếu Nhập Kho')
            sheet.set_column('A:A', 5)
            sheet.set_column('B:B', 15)
            sheet.set_column('C:C', 10)
            sheet.set_column('D:D', 6)
            sheet.set_column('E:E', 7)
            sheet.set_column('F:F', 7)
            sheet.set_column('G:G', 10)
            sheet.set_column('H:H', 15)
            sheet.set_row(12, 30)
            sheet.set_row(13, 50)
            self_data_id = data['form_data']['id']
            header_data = self.env['stock.picking'].sudo().browse(int(self_data_id))
            #header
            company_name = self.env.company.name
            company_street = self.env.company.street
            sheet.write(0, 0, company_name, bold)
            sheet.merge_range(0, 4, 0, 7, '', merge_format)
            sheet.write(0, 4, 'Mẫu số 02 - VT', header_top)
            if company_street:
                sheet.write(1, 0, company_street, bold)
            sheet.merge_range(1, 4, 1, 7, '', merge_format)
            sheet.write(1, 4, '(Ban hành theo Thông tư số 200/TT-BTC', header_top)
            sheet.merge_range(2, 4, 2, 7, '', merge_format)
            sheet.write(2, 4, 'Ngày 22/12/2014 của Bộ Tài Chính)', header_top)

            line_num = 4
            sheet.merge_range(line_num, 0, line_num, 7, '', merge_format)
            sheet.write(line_num, 0, 'PHIẾU NHẬP KHO', header)
            line_num += 1
            sheet.merge_range(line_num, 0, line_num, 7, '', merge_format)
            sheet.write(line_num, 0, 'Ngày %s tháng %s năm %s' % (datetime.utcnow().day, datetime.utcnow().month, datetime.utcnow().year), header1)
            line_num += 1
            sheet.merge_range(line_num, 0, line_num, 7, '', merge_format)
            sheet.write(line_num, 0, 'Số: %s' % header_data.name, header1)
            line_num += 2
            sheet.merge_range(line_num, 0, line_num, 7, '', merge_format)
            sheet.write(line_num, 0, '- Họ và tên người giao: %s' % header_data.partner_id.name, header_text)
            line_num += 1
            sheet.merge_range(line_num, 0, line_num, 7, '', merge_format)
            sheet.write(line_num, 0, '- Theo: %s' % (header_data.note if header_data.note else '...'), header_text)
            line_num += 1
            sheet.merge_range(line_num, 0, line_num, 7, '', merge_format)
            sheet.write(line_num, 0, '- Nhập tại kho: %s   Địa điểm: %s' % (header_data.location_dest_id.report_name if header_data.location_dest_id.report_name else '...'
                                                                            , header_data.location_dest_id.location_name if header_data.location_dest_id.location_name else '...'), header_text)

            line_num += 2
            sheet.merge_range(line_num, 0, line_num + 1, 0, '', merge_format)
            sheet.write(line_num, 0, 'STT', line_header)
            sheet.merge_range(line_num, 1, line_num + 1, 1, '', merge_format)
            sheet.write(line_num, 1, 'Tên, nhãn hiệu, quy cách, phẩm chất vật tư, dụng cụ, sp, hàng hóa', line_header)
            sheet.merge_range(line_num, 2, line_num + 1, 2, '', merge_format)
            sheet.write(line_num, 2, 'Mã số', line_header)
            sheet.merge_range(line_num, 3, line_num + 1, 3, '', merge_format)
            sheet.write(line_num, 3, 'ĐVT', line_header)
            sheet.merge_range(line_num, 4, line_num, 5, '', merge_format)
            sheet.write(line_num, 4, 'Số lượng', line_header)
            sheet.write(line_num, 5, '', line_header)
            sheet.merge_range(line_num, 6, line_num + 1, 6, '', merge_format)
            sheet.write(line_num, 6, 'Đơn giá', line_header)
            sheet.merge_range(line_num, 7, line_num + 1, 7, '', merge_format)
            sheet.write(line_num, 7, 'Thành tiền', line_header)
            line_num += 1
            sheet.write(line_num, 0, '', border_format)
            sheet.write(line_num, 1, '', border_format)
            sheet.write(line_num, 2, '', border_format)
            sheet.write(line_num, 3, '', border_format)
            sheet.write(line_num, 4, 'Theo chứng từ', line_header)
            sheet.write(line_num, 5, 'Thực nhập', line_header)
            sheet.write(line_num, 6, '', line_header)
            sheet.write(line_num, 7, '', border_format)
            line_num += 1
            sheet.write(line_num, 0, 'A', line_header)
            sheet.write(line_num, 1, 'B', line_header)
            sheet.write(line_num, 2, 'C', line_header)
            sheet.write(line_num, 3, 'D', line_header)
            sheet.write(line_num, 4, '1', line_header)
            sheet.write(line_num, 5, '2', line_header)
            sheet.write(line_num, 6, '3', line_header)
            sheet.write(line_num, 7, '4', line_header)
            line_num += 1
            #details
            stt = 1
            sum_total = 0
            lines_data = self.env['stock.move'].sudo().search([('picking_id', '=', header_data.id)])
            for line in lines_data:
                sheet.write(line_num, 0, stt, line_text_center)
                sheet.write(line_num, 1, line.product_id.name if line.product_id.name else '', line_text_format)
                sheet.write(line_num, 2, line.product_id.default_code if line.product_id.default_code else '', line_text_format)
                sheet.write(line_num, 3, line.product_id.uom_id.name if line.product_id.uom_id.name else '', line_text_center)
                sheet.write(line_num, 4, line.product_uom_qty if line.product_uom_qty else '', line_number_format_center)
                sheet.write(line_num, 5, line.product_uom_qty if line.product_uom_qty else '', line_number_format_center)
                sheet.write(line_num, 6, line.purchase_line_id.price_unit if line.purchase_line_id.price_unit else '', line_number_format)
                sheet.write(line_num, 7, line.product_uom_qty * line.purchase_line_id.price_unit if line.product_uom_qty and line.purchase_line_id.price_unit else '', line_number_format)
                sum_total += line.product_uom_qty * line.purchase_line_id.price_unit if line.product_uom_qty and line.purchase_line_id.price_unit else 0
                stt += 1
                line_num += 1

            sheet.write(line_num, 0, '', line_header)
            sheet.write(line_num, 1, 'Cộng', line_header)
            sheet.write(line_num, 2, 'x', line_header)
            sheet.write(line_num, 3, 'x', line_header)
            sheet.write(line_num, 4, 'x', line_header)
            sheet.write(line_num, 5, 'x', line_header)
            sheet.write(line_num, 6, 'x', line_header)
            sheet.write(line_num, 7, sum_total, line_number_format_bold)
            #footer
            line_num += 1
            sheet.merge_range(line_num, 0, line_num, 7, '', merge_format)
            sheet.write(line_num, 0, '- Tổng số tiền (viết bằng chữ): %s đồng' % (capwords(num2words(sum_total, lang='vi')[0:1]) + num2words(sum_total, lang='vi')[1:]), footer_text)
            line_num += 1
            sheet.merge_range(line_num, 0, line_num, 7, '', merge_format)
            sheet.write(line_num, 0, '- Số chứng từ gốc kèm theo:.......', footer_text)
            line_num += 2
            sheet.merge_range(line_num, 0, line_num, 7, '', merge_format)
            sheet.write(line_num, 0,
                        'TP.Hồ Chí Minh, ngày %s tháng %s năm %s' % (datetime.strftime(datetime.utcnow(), '%d')
                                                                     , datetime.strftime(datetime.utcnow(), '%m')
                                                                     , datetime.strftime(datetime.utcnow(), '%Y')),
                        footer_date)
            line_num += 1
            sheet.merge_range(line_num, 0, line_num, 1, '', merge_format)
            sheet.write(line_num, 0, 'Người lập phiếu', signment)
            sheet.merge_range(line_num, 2, line_num, 4, '', merge_format)
            sheet.write(line_num, 2, 'Người giao hàng', signment)
            sheet.merge_range(line_num, 5, line_num, 6, '', merge_format)
            sheet.write(line_num, 5, 'Thủ kho', signment)
            sheet.write(line_num, 7, 'Kế toán trưởng', signment)
            # sheet.write(line_num, 7, 'Giám đốc', signment)
            line_num += 1
            sheet.merge_range(line_num, 0, line_num, 1, '', merge_format)
            sheet.write(line_num, 0, '(Ký, họ tên)', signment_1)
            sheet.merge_range(line_num, 2, line_num, 4, '', merge_format)
            sheet.write(line_num, 2, '(Ký, họ tên)', signment_1)
            sheet.merge_range(line_num, 5, line_num, 6, '', merge_format)
            sheet.write(line_num, 5, '(Ký, họ tên)', signment_1)
            sheet.write(line_num, 7, '(Ký, họ tên)', signment_1)
            line_num += 4
            sheet.merge_range(line_num, 0, line_num, 1, '', merge_format)
            sheet.write(line_num, 0, header_data.write_uid.name, footer_text)
            sheet.merge_range(line_num, 2, line_num, 4, '', merge_format)
            sheet.write(line_num, 2, '', footer_text)
            sheet.merge_range(line_num, 5, line_num, 6, '', merge_format)
            sheet.write(line_num, 5, self.env.company.store_keeper if self.env.company.store_keeper else '', footer_text)
            sheet.write(line_num, 7, self.env.company.chief_accountant if self.env.company.chief_accountant else '', footer_text)
        except Exception as e:
            _logger.error('generate_xlsx_report exception: %s' % e)

