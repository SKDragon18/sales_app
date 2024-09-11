import frappe
import json
from frappe.utils import nowdate
from ..response.response import ApiResponse
from core_api.decorators import api_log
@frappe.whitelist(methods="GET",allow_guest=True)
@api_log("get_order_list")
def get():
    data = frappe.db.sql("""
                         SELECT *
                         FROM `tabSales Order`
                         """, as_dict=True)
    frappe.local.response.update(ApiResponse.success(data=data)) 
    return

@frappe.whitelist(methods="POST")
@api_log("create_order")
def create():
    try:
        #lấy dữ liệu
        data = json.loads(frappe.request.data)
        customer = data.get("customer")
        items = data.get("items")
        
        company = data.get("company")
        shop_id = data.get("shop_id")
        address_line1 = data.get("address_line1")
        address_line2 = data.get("address_line2")
        state = data.get("state")
        city = data.get("city")
        
        if not frappe.db.exists("Customer",customer):
            return{
                "status":"error",
                "message":"Customer does not exists"
            }
        
        if not customer or not items:
            return{
                "status":"error",
                "message":"Don't have customer and items"
            }
            
        sales_order = frappe.get_doc({
            "doctype":"Sales Order",
            "customer":customer,
            "delivery_date":nowdate(),
            "items":[]   
        })
        
        shop = None
        if shop_id or company or address_line1 or address_line2 or state or city:
            filters = []
            if shop_id:
                filters.append(["Shop","shop_id","like", f"%{shop_id}%"])
            if company:
                filters.append(["Shop","company","like", f"%{company}%"])
            if address_line1:
                filters.append(["Shop","address_line1","like", f"%{address_line1}%"])
            if address_line2:
                filters.append(["Shop","address_line2","like", f"%{address_line2}%"])
            if state:
                filters.append(["Shop","state","like", f"%{state}%"])
            if city:
                filters.append(["Shop","city","like", f"%{city}%"])
            shop = frappe.get_list("Shop",
                                        filters = filters,
                                        fields=["*"],
                                        limit=1)
            shop = shop[0]
        warehouse = ''
        if shop:
            warehouse = shop.get("warehouse_for_selling")
        else:
            frappe.local.response.update(ApiResponse.fail(
                message="Please apply information about company and shop_id", 
                error="Not found"))
            return 
        
        sales_order.company = shop.get("company")
        company = frappe.get_doc("Company",shop.get("company"))
        sales_order.selling_price_list = company.custom_price_list
        sales_order.custom_shop = shop.get("name")
        sales_order.company_address = shop.get("address")
        #Thêm sản phẩm
        for item in items:
            sales_order.append("items",{
                "item_code": item.get("item_code"),
                "qty": item.get("qty"),
                "rate":item.get("rate"),
                "warehouse":warehouse
            })
        
        sales_order.insert()
        sales_order.submit()
        frappe.local.response.update(ApiResponse.success(
                    message="Sales Order created successfully", 
                    data={
                        "sales_order_name":sales_order.name,
                        "warehouse": warehouse
                    }))
        return 
    except Exception as e:
        frappe.log_error(frappe.get_traceback(),"Sales Order Creation Error")
        frappe.local.response.update(ApiResponse.fail(
                    message="Exception Error", 
                    error=str(e)))
        return 

            
        