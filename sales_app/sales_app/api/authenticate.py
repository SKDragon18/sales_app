import frappe
import json
from frappe import auth

@frappe.whitelist(methods="POST",allow_guest=True)
def login():
    try:
        data = json.loads(frappe.request.data)
        user = data.get("user")
        pwd = data.get("pwd")
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=user, pwd = pwd)
        login_manager.post_login()
    except frappe.exceptions.AuthenticationError:
        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key":0,
            "message":"Authentication Error!"
        }
        return 
    api_generate, api_key = generate_keys(frappe.session.user)
    user = frappe.get_doc("User",frappe.session.user)
    frappe.response["message"]={
        "success_key":1,
        "message":"Authentication Success",
        "sid":frappe.session.sid,
        "api_key":api_key,
        "api_secret":api_generate,
        "username":user.username,
        "email":user.email
    }
def generate_keys(user):
    user_details = frappe.get_doc('User', user)
    api_secret = frappe.generate_hash(length=15)
    
    if not user_details.api_key:
        api_key = frappe.generate_hash(length=15)
        user_details.api_key = api_key
    user_details.api_secret = api_secret
    user_details.save()
    return api_secret, user_details.api_key