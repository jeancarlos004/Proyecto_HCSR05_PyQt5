import bcrypt

pwd = "admin123".encode("utf-8")
hashed = bcrypt.hashpw(pwd, bcrypt.gensalt()).decode("utf-8")
print(hashed)
 
