"""
Odoo MCP - Gold Tier Integration for Personal AI Employee
Connects AI Employee to Odoo Accounting System
"""

import os
import sys
import xmlrpc.client
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from .env
ODOO_URL = os.getenv("ODOO_URL", "http://localhost:8069")
ODOO_DB = os.getenv("ODOO_DB", "odoo_ai_employee")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD", "")

# Vault paths
VAULT_BASE = os.getenv("VAULT_BASE", r"C:\Users\Iqra Traders\Documents\AI_Employee_Vault")
LOGS_DIR = os.path.join(VAULT_BASE, "Logs")
NEEDS_ACTION_DIR = os.path.join(VAULT_BASE, "Needs_Action")


def get_odoo_connection():
    """Establish connection to Odoo via XML-RPC using password authentication"""
    print(f"\n[DEBUG] Connecting to Odoo...")
    print(f"[DEBUG] URL: {ODOO_URL}")
    print(f"[DEBUG] Database: {ODOO_DB}")
    print(f"[DEBUG] Username: {ODOO_USERNAME}")

    # Mask password for security (show first char and last 2 chars only)
    if ODOO_PASSWORD and len(ODOO_PASSWORD) >= 3:
        masked_pwd = ODOO_PASSWORD[0] + "*" * (len(ODOO_PASSWORD) - 3) + ODOO_PASSWORD[-2:]
    elif ODOO_PASSWORD:
        masked_pwd = "*" * len(ODOO_PASSWORD)
    else:
        masked_pwd = "(empty)"
    print(f"[DEBUG] Password: {masked_pwd}")

    try:
        # Common authentication endpoint
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")

        # Authenticate with password and get uid
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})

        print(f"[DEBUG] Authentication result (uid): {uid}")
        print(f"[DEBUG] uid type: {type(uid).__name__}")

        # Check if authentication failed
        if not uid or uid is False:
            print(f"\n[ERROR] Authentication failed!")
            print(f"[ERROR] Odoo returned uid: {uid}")
            print(f"\n[HELP] Possible causes:")
            print(f"  1. Incorrect password in .env file")
            print(f"  2. Odoo server is not running at {ODOO_URL}")
            print(f"  3. Database '{ODOO_DB}' does not exist")
            print(f"  4. Username '{ODOO_USERNAME}' is incorrect")
            print(f"\n[HELP] Check your .env file at:")
            print(f"  C:\\Users\\Iqra Traders\\Documents\\ai_employee\\.env")
            return None, None

        # Authentication succeeded - uid is a number
        print(f"\n[SUCCESS] Authentication successful! uid={uid}")

        # Object endpoint for operations
        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

        return uid, models

    except Exception as e:
        print(f"\n[ERROR] Connection failed: {e}")
        print(f"[DEBUG] Full error type: {type(e).__name__}")
        return None, None


def test_connection():
    """Test the Odoo connection by fetching invoices"""
    uid, models = get_odoo_connection()
    if not uid:
        return False

    try:
        print(f"\n[DEBUG] Testing connection with search_read...")

        # Test call - fetch invoices
        result = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'account.move', 'search_read',
            [[['move_type', '=', 'out_invoice']]],
            {'fields': ['name', 'partner_id', 'amount_total', 'invoice_date_due', 'payment_state'], 'limit': 5}
        )

        print(f"[DEBUG] Test query returned {len(result)} invoices")
        if result:
            print(f"[DEBUG] First invoice: {result[0]}")

        print("\n[SUCCESS] Connection test passed!")
        return True

    except Exception as e:
        print(f"\n[ERROR] Test query failed: {e}")
        return False


def ensure_directories():
    """Create necessary directories if they don't exist"""
    os.makedirs(LOGS_DIR, exist_ok=True)
    os.makedirs(NEEDS_ACTION_DIR, exist_ok=True)


def log_action(action, details):
    """Log an action to the Logs directory"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOGS_DIR, f"odoo_action_{timestamp}.log")

    log_entry = f"""---
type: odoo_log
timestamp: {datetime.now().isoformat()}
action: {action}
status: completed
---
## Action: {action}
{details}
"""
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(log_entry)

    print(f"Logged to: {log_file}")


def get_company_currency(uid, models):
    """Get the company's default currency ID"""
    company = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.company', 'search_read',
        [[]],
        {'fields': ['currency_id'], 'limit': 1}
    )
    
    if company and len(company) > 0:
        # currency_id is returned as [id, name]
        currency_id = company[0]['currency_id'][0]
        currency_name = company[0]['currency_id'][1]
        print(f"[DEBUG] Company default currency: {currency_name} (ID: {currency_id})")
        return currency_id
    
    print("[WARNING] Could not get company currency, using None")
    return None


def create_invoice(customer_name, amount, description):
    """
    Create a new customer invoice in Odoo (saved as draft)
    Uses company's default currency automatically.

    Args:
        customer_name: Name of the customer
        amount: Invoice amount
        description: Invoice line description
    """
    uid, models = get_odoo_connection()
    if not uid:
        return None

    try:
        # Find or create customer
        partner_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            "res.partner",
            "search",
            [[["name", "=", customer_name]]]
        )

        if not partner_id:
            # Create new customer
            partner_id = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                "res.partner",
                "create",
                [{
                    "name": customer_name,
                    "company_type": "company",
                }]
            )
            print(f"Created new customer: {customer_name}")
        else:
            partner_id = partner_id[0]

        # Get company's default currency
        currency_id = get_company_currency(uid, models)

        # Create invoice (account.move in Odoo 13+)
        invoice_data = {
            "move_type": "out_invoice",
            "partner_id": partner_id,
            "invoice_date": datetime.now().strftime("%Y-%m-%d"),
            "currency_id": currency_id,
            "invoice_line_ids": [(0, 0, {
                "name": description,
                "price_unit": amount,
                "quantity": 1,
            })],
        }

        invoice_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            "account.move",
            "create",
            [invoice_data]
        )

        # Get invoice number
        invoice = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            "account.move",
            "read",
            [[invoice_id], ["name"]]
        )
        invoice_number = invoice[0].get("name", "Draft")

        details = f"""
Invoice Created:
- Invoice Number: {invoice_number}
- Customer: {customer_name}
- Amount: {amount}
- Description: {description}
- Status: Draft
"""
        log_action("CREATE_INVOICE", details)

        print(f"Invoice created successfully: {invoice_number}")
        return invoice_id

    except Exception as e:
        print(f"Error creating invoice: {e}")
        log_action("CREATE_INVOICE_ERROR", str(e))
        return None


def get_unpaid_invoices():
    """
    Fetch all unpaid invoices from Odoo
    Save summary to Needs_Action folder
    """
    uid, models = get_odoo_connection()
    if not uid:
        return []

    try:
        # Search for unpaid invoices (state in ['posted', 'draft'] with outstanding amount)
        unpaid_invoices = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            "account.move",
            "search",
            [[
                ["move_type", "=", "out_invoice"],
                ["state", "!=", "cancel"],
                ["payment_state", "!=", "paid"]
            ]]
        )

        if not unpaid_invoices:
            print("No unpaid invoices found.")
            return []

        # Read invoice details
        invoices_data = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            "account.move",
            "read",
            [unpaid_invoices, ["name", "partner_id", "amount_total", "invoice_date_due", "payment_state"]]
        )

        # Format report
        report_lines = []
        for inv in invoices_data:
            partner_name = inv.get("partner_id", [None, "Unknown"])[1] if inv.get("partner_id") else "Unknown"
            due_date = inv.get("invoice_date_due", "N/A") or "N/A"
            report_lines.append({
                "name": inv.get("name", "N/A"),
                "customer": partner_name,
                "amount": inv.get("amount_total", 0),
                "due_date": due_date,
                "state": inv.get("payment_state", "unknown")
            })

        # Create markdown report
        report_content = f"""---
type: odoo_report
generated: {datetime.now().isoformat()}
status: pending
---
## Unpaid Invoices Report

| Invoice | Customer | Amount | Due Date |
|---------|----------|--------|----------|
"""
        for inv in report_lines:
            report_content += f"| {inv['name']} | {inv['customer']} | {inv['amount']:.2f} | {inv['due_date']} |\n"

        report_content += f"\n**Total Unpaid:** {len(report_lines)} invoices\n"

        # Save to Needs_Action folder
        report_file = os.path.join(NEEDS_ACTION_DIR, "ODOO_unpaid_invoices.md")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        details = f"""
Unpaid Invoices Report Generated:
- Total Unpaid: {len(report_lines)}
- Report saved to: {report_file}
"""
        log_action("GET_UNPAID_INVOICES", details)

        print(f"Unpaid invoices report saved to: {report_file}")
        return report_lines

    except Exception as e:
        print(f"Error fetching unpaid invoices: {e}")
        log_action("GET_UNPAID_INVOICES_ERROR", str(e))
        return []


def weekly_accounting_report():
    """
    Get all invoices from last 7 days
    Calculate total revenue
    List paid and unpaid invoices
    """
    uid, models = get_odoo_connection()
    if not uid:
        return None

    try:
        # Calculate date range (last 7 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        # Search for invoices in date range
        weekly_invoices = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            "account.move",
            "search",
            [[
                ["move_type", "=", "out_invoice"],
                ["invoice_date", ">=", start_date.strftime("%Y-%m-%d")],
                ["invoice_date", "<=", end_date.strftime("%Y-%m-%d")]
            ]]
        )

        if not weekly_invoices:
            print("No invoices found in the last 7 days.")
            # Still create an empty report
            invoices_data = []
        else:
            # Read invoice details
            invoices_data = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                "account.move",
                "read",
                [weekly_invoices, ["name", "partner_id", "amount_total", "invoice_date", "payment_state"]]
            )

        # Process data
        paid_invoices = []
        unpaid_invoices = []
        total_revenue = 0

        for inv in invoices_data:
            partner_name = inv.get("partner_id", [None, "Unknown"])[1] if inv.get("partner_id") else "Unknown"
            amount = inv.get("amount_total", 0)
            state = inv.get("payment_state", "not_paid")

            invoice_info = {
                "name": inv.get("name", "N/A"),
                "customer": partner_name,
                "amount": amount,
                "date": inv.get("invoice_date", "N/A")
            }

            if state == "paid":
                paid_invoices.append(invoice_info)
                total_revenue += amount
            else:
                unpaid_invoices.append(invoice_info)

        # Create report
        report_date = datetime.now().strftime("%Y%m%d")
        report_content = f"""---
type: weekly_accounting_report
generated: {datetime.now().isoformat()}
period_start: {start_date.strftime("%Y-%m-%d")}
period_end: {end_date.strftime("%Y-%m-%d")}
---
## Weekly Accounting Report

**Period:** {start_date.strftime("%B %d, %Y")} - {end_date.strftime("%B %d, %Y")}

### Summary
- **Total Revenue:** {total_revenue:,.2f} PKR
- **Paid Invoices:** {len(paid_invoices)}
- **Unpaid Invoices:** {len(unpaid_invoices)}

### Paid Invoices
| Invoice | Customer | Amount | Date |
|---------|----------|--------|------|
"""
        for inv in paid_invoices:
            report_content += f"| {inv['name']} | {inv['customer']} | {inv['amount']:.2f} | {inv['date']} |\n"

        if not paid_invoices:
            report_content += "| - | - | - | - |\n"

        report_content += "\n### Unpaid Invoices\n| Invoice | Customer | Amount | Date |\n|---------|----------|--------|------|\n"

        for inv in unpaid_invoices:
            report_content += f"| {inv['name']} | {inv['customer']} | {inv['amount']:.2f} | {inv['date']} |\n"

        if not unpaid_invoices:
            report_content += "| - | - | - | - |\n"

        # Save report
        report_file = os.path.join(VAULT_BASE, f"WEEKLY_ACCOUNTING_{report_date}.md")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        details = f"""
Weekly Accounting Report Generated:
- Period: {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}
- Total Revenue: {total_revenue:,.2f} PKR
- Paid: {len(paid_invoices)}, Unpaid: {len(unpaid_invoices)}
- Report saved to: {report_file}
"""
        log_action("WEEKLY_ACCOUNTING_REPORT", details)

        print(f"Weekly report saved to: {report_file}")
        return report_content

    except Exception as e:
        print(f"Error generating weekly report: {e}")
        log_action("WEEKLY_ACCOUNTING_REPORT_ERROR", str(e))
        return None


def check_overdue_invoices():
    """
    Find all overdue invoices
    Create alert file in Needs_Action folder
    """
    uid, models = get_odoo_connection()
    if not uid:
        return []

    try:
        today = datetime.now().strftime("%Y-%m-%d")

        # Search for overdue unpaid invoices
        overdue_invoices = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            "account.move",
            "search",
            [[
                ["move_type", "=", "out_invoice"],
                ["state", "!=", "cancel"],
                ["payment_state", "!=", "paid"],
                ["invoice_date_due", "<", today]
            ]]
        )

        if not overdue_invoices:
            print("No overdue invoices found.")
            return []

        # Read invoice details
        invoices_data = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            "account.move",
            "read",
            [overdue_invoices, ["name", "partner_id", "amount_total", "invoice_date_due", "payment_state"]]
        )

        # Process data
        overdue_list = []
        total_overdue = 0

        for inv in invoices_data:
            partner_name = inv.get("partner_id", [None, "Unknown"])[1] if inv.get("partner_id") else "Unknown"
            amount = inv.get("amount_total", 0)
            due_date = inv.get("invoice_date_due", "Unknown")

            overdue_list.append({
                "name": inv.get("name", "N/A"),
                "customer": partner_name,
                "amount": amount,
                "due_date": due_date,
                "days_overdue": (datetime.now() - datetime.strptime(str(due_date), "%Y-%m-%d")).days if due_date != "Unknown" else 0
            })
            total_overdue += amount

        # Create alert
        alert_content = f"""---
type: alert
severity: high
generated: {datetime.now().isoformat()}
action_required: true
---
# ALERT: Overdue Invoices

**Total Overdue Amount:** {total_overdue:,.2f} PKR  
**Number of Overdue Invoices:** {len(overdue_list)}  
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Overdue Invoices Details

| Invoice | Customer | Amount | Due Date | Days Overdue |
|---------|----------|--------|----------|--------------|
"""
        for inv in overdue_list:
            alert_content += f"| {inv['name']} | {inv['customer']} | {inv['amount']:.2f} | {inv['due_date']} | {inv['days_overdue']} |\n"

        alert_content += f"""

## Recommended Actions
1. Send payment reminder emails to customers
2. Follow up with phone calls for high-value invoices
3. Consider late payment fees if applicable
4. Update collection status in CRM
"""

        # Save alert
        alert_file = os.path.join(NEEDS_ACTION_DIR, "ALERT_overdue_invoices.md")
        with open(alert_file, "w", encoding="utf-8") as f:
            f.write(alert_content)

        details = f"""
Overdue Invoices Alert Generated:
- Total Overdue: {total_overdue:,.2f} PKR
- Count: {len(overdue_list)} invoices
- Alert saved to: {alert_file}
"""
        log_action("CHECK_OVERDUE_INVOICES", details)

        print(f"ALERT: {len(overdue_list)} overdue invoices found!")
        print(f"Alert saved to: {alert_file}")
        return overdue_list

    except Exception as e:
        print(f"Error checking overdue invoices: {e}")
        log_action("CHECK_OVERDUE_INVOICES_ERROR", str(e))
        return []


def main_menu():
    """Main interactive menu"""
    ensure_directories()

    print("\n" + "="*50)
    print("  ODOO MCP - Gold Tier Accounting Integration")
    print("="*50)
    print(f"  Odoo URL: {ODOO_URL}")
    print(f"  Database: {ODOO_DB}")
    print(f"  Vault: {VAULT_BASE}")
    print("="*50)

    while True:
        print("\nType 1 - Create Invoice")
        print("Type 2 - Get Unpaid Invoices")
        print("Type 3 - Weekly Report")
        print("Type 4 - Check Overdue")
        print("Type 5 - Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            print("\n--- Create Invoice ---")
            customer = input("Customer Name: ").strip()
            try:
                amount = float(input("Amount: ").strip())
            except ValueError:
                print("Invalid amount. Please enter a number.")
                continue
            description = input("Description: ").strip()

            create_invoice(customer, amount, description)

        elif choice == "2":
            print("\n--- Getting Unpaid Invoices ---")
            get_unpaid_invoices()

        elif choice == "3":
            print("\n--- Generating Weekly Accounting Report ---")
            weekly_accounting_report()

        elif choice == "4":
            print("\n--- Checking Overdue Invoices ---")
            check_overdue_invoices()

        elif choice == "5":
            print("\nExiting Odoo MCP. Goodbye!")
            sys.exit(0)

        else:
            print("\nInvalid choice. Please enter 1-5.")


if __name__ == "__main__":
    main_menu()
