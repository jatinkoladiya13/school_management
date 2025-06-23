from bson import ObjectId

def convert_object_id(data):
    if isinstance(data, dict):
        return {k: convert_object_id(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_object_id(i) for i in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

def calculate_grade(percentage):
        if percentage >= 90:
            return 'A1'
        elif percentage >= 80:
            return 'A2'   
        elif percentage >= 70:
            return 'B1'  
        elif percentage >= 60:
            return 'B2'  
        elif percentage >= 50:
            return 'C1'  
        elif percentage >= 40:
            return 'C2'  
        elif percentage >= 33:
            return 'D'  
        elif percentage >= 20:
            return 'E1'  
        elif percentage >= 0:
            return 'E2'  