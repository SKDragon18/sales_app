import frappe
import json
from frappe.utils import nowdate
from ..response.response import ApiResponse
from core_api.decorators import api_log
@frappe.whitelist(methods="POST")
@api_log("create_delivery")
def create(sales_order_name):
    try:
        sales_order = frappe.get_doc("Sales Order", sales_order_name)
        
        if sales_order.docstatus != 1: #chưa submit
            frappe.local.response.update(ApiResponse.fail(
                    message="Sales Order must be submitted before", 
                    error="Not submit"))
            return
        
        delivery_note = frappe.new_doc("Delivery Note")
        delivery_note.customer = sales_order.customer
        delivery_note.company = sales_order.company
        delivery_note.company_address = sales_order.company_address
        delivery_note.selling_price_list = sales_order.selling_price_list
        delivery_note.posting_date = nowdate()
        
        for item in sales_order.items:
            delivery_note.append("items",{
                "item_code": item.item_code,
                "qty": item.qty,
                "rate": item.rate,
                "warehouse": item.warehouse,
                "so_detail": item.name,
                "against_sales_order": sales_order_name
            })
        
        delivery_note.insert()
        delivery_note.submit()
        frappe.local.response.update(ApiResponse.success(
                    message="Delivery Note created successfully", 
                    data={
                        "delivery_note_name":delivery_note.name
                    }))
        return 
    
    except frappe.DoesNotExistError:
        frappe.local.response.update(ApiResponse.fail(
                    message=f"Sales Order {sales_order_name} does not exist", 
                    error="Not found"))
        return
    except Exception as e:
        frappe.log_error(frappe.get_traceback(),"Delivery Note Creation Error")
        frappe.local.response.update(ApiResponse.fail(
                    message="Exception Error", 
                    error=str(e)))
        return