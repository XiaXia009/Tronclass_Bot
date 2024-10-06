import json
filepath = './userdata.json'

def load_data(filepath='./userdata.json'):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_data(data, filepath='./userdata.json'):
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def add_user(student_id, password, user_id, filepath='./userdata.json'):
    data = load_data(filepath)
    user_found = False

    for user in data:
        if user["Student_ID"] == student_id:
            user["Password"] = password
            user_found = True
            break

    if not user_found:
        new_user = {"Student_ID": student_id, "Password": password, "User_ID": user_id}
        data.append(new_user)

    save_data(data, filepath)
    
    if user_found:
        print(f"User {student_id} updata.")
    else:
        print(f"User {student_id} added.")

def del_user(user_id, filepath='./userdata.json'):
    data = load_data(filepath)
    updated_data = []
    deleted_student_id = None
    
    for user in data:
        if user["User_ID"] == user_id:
            deleted_student_id = user["Student_ID"]
        else:
            updated_data.append(user)
    
    save_data(updated_data, filepath)
    
    if deleted_student_id:
        print(f"User {deleted_student_id} del")
        return deleted_student_id
    else:
        return None

def search(user_id, filepath='./userdata.json'):
    data = load_data(filepath)
    user_found = False

    for user in data:
        if user["User_ID"] == user_id:
            username = user["Student_ID"]
            password = user["Password"]
            try:
                return username, password
            except:
                return None, None
            
def put(filepath='./userdata.json'):
    data = load_data(filepath)
    for user in data:
        yield user["Student_ID"], user["Password"], user["User_ID"]