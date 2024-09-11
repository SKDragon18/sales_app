import frappe
import json
from frappe.utils import nowdate, validate_email_address, random_string
from ..utils.check import is_valid_email, is_valid_phone
@frappe.whitelist(methods="POST",allow_guest=True)
def create_customer():
    try:
        data = json.loads(frappe.request.data)
        email = data.get("email")
        phone_number = data.get("phone_number")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        address_line1 = data.get("address_line1")
        address_line2 = data.get("address_line2")
        country = data.get("country")
        city = data.get("city")
        
        if phone_number:
            if not is_valid_phone(phone_number):
                return {
                    "status":"failed",
                    "message":"Phone is not valid"
                } 
            if frappe.db.exists("User",{"phone":phone_number}):
                return {
                    "status":"failed",
                    "message":"Phone has existed"
                }
            if frappe.db.exists("Customer",{"mobile_no":phone_number}):
                return {
                    "status":"failed",
                    "message":"Phone has existed"
                }
            
            
        if email:
            if not is_valid_email(email):
                return{
                    "status":"failed",
                    "message":"Email is not valid"
                }
            if frappe.db.exists("User",{"email":email}):
                return{
                    "status":"failed",
                    "message":"Email has existed"
                }
            
        else:
            email = f"{phone_number}@example.com"
    
        user = frappe.new_doc("User")
        user.email = email
        user.first_name = first_name if first_name else "Customer"
        user.last_name = last_name if last_name else phone_number
        user.phone = phone_number
        user.username = email
        user.send_welcome_email = 0
        user.append("roles",{
            "role":"Customer"
        })
        user.insert(ignore_permissions = True)
        
        #tạo mật khẩu
        password = random_string(10)
        user.new_password = password
        user.save()
        
        
        customer = frappe.new_doc("Customer")
        # customer.customer_name = f"{first_name}{last_name}" if first_name and last_name else phone_number
        customer.customer_name = email
        customer.customer_group = "Individual"
        customer.territory = "All Territories"
        customer.mobile_no = phone_number
        customer.append("portal_users",{
            "user": email
        })
        customer.insert(ignore_permissions = True)
        
        if address_line1 and country:
            address = frappe.new_doc("Address")
            address.address_title = customer.name
            address.address_type  = "Shipping"
            address.address_line1 = address_line1
            address.address_line2 = address_line2
            address.city = city
            address.country = country
            address.email_id = email
            address.phone = phone_number
            address.append("links",{
                "link_doctype":"Customer",
                "link_name": customer.name
            })
            address.insert()
        
        return {
            "status": "success",
            "message": "User and Customer created successfully",
            "user_id": user.name,
            "password": password,
            "customer_id": customer.name
        }
    except Exception as e:
        return{
            "status":"failed",
            "message":str(e)
        }