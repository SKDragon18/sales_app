import frappe
import json
from frappe.utils import nowdate
from ..response.response import ApiResponse
from core_api.decorators import api_log
@frappe.whitelist(methods="POST")
@api_log("create_invoice")
def create(delivery_note_name):
    try:
        delivery_note = frappe.get_doc("Delivery Note", delivery_note_name)
        if delivery_note.docstatus != 1:
            frappe.local.response.update(ApiResponse.fail(
                    message="Delivery Note must be submitted before", 
                    error="Not submit"))
            return
        
        sales_invoice = frappe.new_doc("Sales Invoice")
        sales_invoice.customer = delivery_note.customer
        sales_invoice.company = delivery_note.company
        sales_invoice.company_address = delivery_note.company_address
        sales_invoice.selling_price_list = delivery_note.selling_price_list
        sales_invoice.due_date = nowdate()
        sales_invoice.posting_date = nowdate()
        
        for item in delivery_note.items:
            if item.against_sales_order and item.so_detail:
                sales_invoice.append("items",{
                    "item_code": item.item_code,
                    "qty": item.qty,
                    "rate": item.rate,
                    "warehouse": item.warehouse,
                    "delivery_note": delivery_note_name,
                    "dn_detail":item.name,
                    "sales_order": item.against_sales_order,
                    "so_detail": item.so_detail
                })
            else:
                frappe.local.response.update(ApiResponse.fail(
                    message=f"Sales Order is mandatory for Item {item.item_code}", 
                    error="Not found"))
                return
        
        sales_invoice.insert()
        sales_invoice.submit()
        frappe.local.response.update(ApiResponse.success(
                    message="Sales Invoice created successfully", 
                    data={
                        "sales_invoice_name": sales_invoice.name
                    }))
        return 
        
    except frappe.DoesNotExistError:
        frappe.local.response.update(ApiResponse.fail(
                    message=f"Delivery Note {delivery_note_name} does not exist", 
                    error="Not found"))
        return
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Sales Invoice Creation Error")
        frappe.local.response.update(ApiResponse.fail(
                    message="Exception Error", 
                    error=str(e)))
        return