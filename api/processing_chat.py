from model_service import ModelService

def process_follow_up_message(chat_history, user_query, file_data):
    model_service = ModelService()
    relevant_files = model_service.get_relevant_files(file_data, user_query)
    relevant_file_data = [{file["path"]: file["code"]} for file in file_data if file["path"] in relevant_files]
    model_response = model_service.generate_response(relevant_file_data, chat_history)
    return model_response

