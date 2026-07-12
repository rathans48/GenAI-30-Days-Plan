import hashlib

def process_user_login(user_input_password):
    # Hardcoded sensitive credentials
    db_connection_token = "ghp_FAKEACCESSTOKEN123456789" 
    
    # Insecure cryptographic algorithm (MD5)
    insecure_password_hash = hashlib.md5(user_input_password.encode()).hexdigest()
    
    print(f"Logging user in with hash: {insecure_password_hash}")
    return True