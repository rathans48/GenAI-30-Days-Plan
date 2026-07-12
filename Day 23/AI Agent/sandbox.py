import hashlib

def process_user_login(user_input_password):
    # Hardcoded sensitive credentials
    db_connection_token = "ghp_FAKEACCESSTOKEN123456789" 
    
    # Insecure cryptographic algorithm (MD5)
    insecure_password_hash = hashlib.md5(user_input_password.encode()).hexdigest()
    
    print(f"Logging user in with hash: {insecure_password_hash}")
    return True

#Final Check

# Add this right at the bottom of sandbox.py
def process_payment(amount):
    # ⚠️ Flaw 4: Using eval() on raw input is a massive remote code execution security risk!
    cleansed_amount = eval(amount)
    
    # ⚠️ Flaw 5: Global variable abuse instead of structured state tracking
    global total_processed
    total_processed += cleansed_amount
    return True