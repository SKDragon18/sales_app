import frappe
import json
from frappe.utils import nowdate
from ..response.response import ApiResponse
from core_api.decorators import api_log
@frappe.whitelist(methods="POST")
@api_log("pay_with_cash")
def pay_with_cash(sales_invoice_name):
    try:
        sales_invoice = frappe.get_doc("Sales Invoice", sales_invoice_name)
        if sales_invoice.docstatus != 1:
            frappe.local.response.update(ApiResponse.fail(
                    message="Sales Invoice must be submitted before", 
                    error="Not submit"))
            return
        
        payment_entry = frappe.new_doc("Payment Entry")
        payment_entry.payment_type = "Receive"
        
        payment_entry.party_type = "Customer"
        payment_entry.party = sales_invoice.customer
        
        payment_entry.received_amount = sales_invoice.grand_total
        payment_entry.paid_amount = sales_invoice.grand_total
        payment_entry.payment_date = nowdate()
        payment_entry.payment_mode = "Cash"
        # payment_entry.paid_from = "Debtors - CyberTech"
        # payment_entry.paid_to = "Cash - CyberTech"
        payment_entry.company = sales_invoice.company
        company = frappe.get_doc("Company",payment_entry.company)
        payment_entry.paid_to = company.default_cash_account
        payment_entry.target_exchange_rate=1
        payment_entry.source_exchange_rate=1
        payment_entry.append("references",{
            "reference_doctype": "Sales Invoice",
            "reference_name": sales_invoice.name,
            "amount": sales_invoice.grand_total,
            "outstanding_amount": sales_invoice.outstanding_amount,
            "allocated_amount": sales_invoice.grand_total
        })
        
        payment_entry.insert()
        payment_entry.submit()
        frappe.local.response.update(ApiResponse.success(
                    message="Payment Entry created successfully", 
                    data={
                        "payment_entry_name": payment_entry.name
                    }))
        return 
    except frappe.DoesNotExistError:
        frappe.local.response.update(ApiResponse.fail(
                    message= f"Sales Invoice {sales_invoice_name} does not exist", 
                    error="Not found"))
        return
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(),"Payment Entry Create Error")
        frappe.local.response.update(ApiResponse.fail(
                    message="Exception Error", 
                    error=str(e)))
        return
    