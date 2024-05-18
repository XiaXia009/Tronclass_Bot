import json

def load_data(filepath='userdata.json'):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_data(data, filepath='userdata.json'):
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def add_user(student_id, password, filepath='userdata.json'):
    data = load_data(filepath)
    user_found = False

    for user in data:
        if user["Student_ID"] == student_id:
            user["Password"] = password
            user_found = True
            break

    if not user_found:
        new_user = {"Student_ID": student_id, "Password": password}
        data.append(new_user)

    save_data(data, filepath)
    
    if user_found:
        print(f"User {student_id} updata.")
    else:
        print(f"User {student_id} added.")

def del_user(student_id, filepath='userdata.json'):
    data = load_data(filepath)
    updated_data = [user for user in data if user["Student_ID"] != student_id]
    save_data(updated_data, filepath)
    print(f"User {student_id} deleted.")
