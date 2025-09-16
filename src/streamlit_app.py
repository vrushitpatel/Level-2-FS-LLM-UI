import streamlit as st
import requests

st.title("Customer Relationship Management System")

BASE_URL = "https://vrush1t-level-2-fs-llm-api.hf.space"  # Matches localhost Port or Hugging Face Embedded  Direct URL

def get_customers():
    try:
        response = requests.get(f"{BASE_URL}/customers", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        st.error(f"Failed to fetch customers: {exc}")
        return []

def get_next_id(customers):
    if not customers:
        return 1
    try:
        return max(c.get("id", 0) for c in customers) + 1
    except Exception:
        return 1

# ---- Styles ----
st.markdown(
    """
    <style>
    .card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px 14px;
        background-color: #ffffff;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        margin-bottom: 10px;
    }
    .card h4 { margin: 0 0 6px 0; }
    .muted { color: #6b7280; font-size: 13px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- View Customers (as cards) ----
st.subheader("Customers")
col_left, _ = st.columns([1, 5])
with col_left:
    refresh = st.button("Refresh")

if refresh or "_customers" not in st.session_state:
    st.session_state["_customers"] = get_customers()

customers = st.session_state.get("_customers", [])

if not customers:
    st.info("No customers yet. Create your first customer below.")
else:
    cols = st.columns(3)
    for idx, c in enumerate(customers):
        with cols[idx % 3]:
            st.markdown(
                f"""
                <div class=\"card\">
                    <h4>{c.get('name','Unnamed')}</h4>
                    <div class=\"muted\">ID #{c.get('id','-')}</div>
                    <div>Email: {c.get('email','—')}</div>
                    <div>Phone: {c.get('phone','—')}</div>
                    <div>Address: {c.get('address','—')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.divider()

# ---- Create Customer ----
st.subheader("Create Customer")
existing_customers = customers
default_id = get_next_id(existing_customers)
with st.form("create_customer_form"):
    new_id = st.number_input("ID", min_value=1, value=default_id, step=1)
    name = st.text_input("Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    address = st.text_input("Address")
    submitted = st.form_submit_button("Create")

    if submitted:
        payload = {
            "id": int(new_id),
            "name": name,
            "email": email,
            "phone": phone if phone else None,
            "address": address if address else None,
        }
        try:
            resp = requests.post(f"{BASE_URL}/customers", json=payload, timeout=5)
            if resp.status_code == 200:
                st.success("Customer created successfully")
                st.session_state["_customers"] = get_customers()
            else:
                st.error(f"Create failed: {resp.status_code} {resp.text}")
        except requests.RequestException as exc:
            st.error(f"Create failed: {exc}")

st.divider()

# ---- Update Customer (dropdown) ----
st.subheader("Update Customer")
customer_options = [f"#{c['id']} - {c['name']}" for c in customers] if customers else []
selected_update = st.selectbox(
    "Select a customer",
    options=customer_options,
    index=0 if customer_options else None,
    placeholder="Pick a customer to update",
)

selected_customer = None
if selected_update and customers:
    try:
        sel_id = int(selected_update.split(" - ")[0].replace("#", "").strip())
        selected_customer = next((c for c in customers if c.get("id") == sel_id), None)
    except Exception:
        selected_customer = None

if selected_customer:
    with st.form("update_customer_form"):
        upd_name = st.text_input("Name", value=selected_customer.get("name", ""))
        upd_email = st.text_input("Email", value=selected_customer.get("email", ""))
        upd_phone = st.text_input("Phone", value=selected_customer.get("phone", "") or "")
        upd_address = st.text_input("Address", value=selected_customer.get("address", "") or "")
        update_submit = st.form_submit_button("Update")

        if update_submit:
            payload = {
                "id": int(selected_customer.get("id")),
                "name": upd_name,
                "email": upd_email,
                "phone": upd_phone if upd_phone else None,
                "address": upd_address if upd_address else None,
            }
            try:
                resp = requests.put(f"{BASE_URL}/customers/{int(selected_customer.get('id'))}", json=payload, timeout=5)
                if resp.status_code == 200:
                    st.success("Customer updated successfully")
                    st.session_state["_customers"] = get_customers()
                elif resp.status_code == 404:
                    st.error("Customer not found")
                else:
                    st.error(f"Update failed: {resp.status_code} {resp.text}")
            except requests.RequestException as exc:
                st.error(f"Update failed: {exc}")
else:
    st.caption("Select a customer to edit.")

st.divider()

# ---- Delete Customer (dropdown) ----
st.subheader("Delete Customer")
delete_options = [f"#{c['id']} - {c['name']}" for c in customers] if customers else []
selected_delete = st.selectbox(
    "Select a customer to delete",
    options=delete_options,
    index=0 if delete_options else None,
    placeholder="Pick a customer",
    key="delete_select",
)

if selected_delete and customers:
    try:
        del_id = int(selected_delete.split(" - ")[0].replace("#", "").strip())
    except Exception:
        del_id = None

    col_a, col_b = st.columns([1, 3])
    with col_a:
        confirm = st.button("Delete", type="primary")
    with col_b:
        st.warning("This action cannot be undone.")

    if confirm and del_id is not None:
        try:
            resp = requests.delete(f"{BASE_URL}/customers/{int(del_id)}", timeout=5)
            if resp.status_code == 200:
                st.success("Customer deleted successfully")
                st.session_state["_customers"] = get_customers()
            elif resp.status_code == 404:
                st.error("Customer not found")
            else:
                st.error(f"Delete failed: {resp.status_code} {resp.text}")
        except requests.RequestException as exc:
            st.error(f"Delete failed: {exc}")
else:
    st.caption("Select a customer to delete.")